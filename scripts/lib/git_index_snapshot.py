#!/usr/bin/env python3
"""Run scheduler generated-artifact checks from one immutable Git tree."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


OID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DRIVE_RE = re.compile(r"^[A-Za-z]:")
REGULAR_MODES = {"100644", "100755"}
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
COMMON_PATHS = {"scripts/lib/git_index_snapshot.py", "pyproject.toml", "uv.lock"}
INVENTORY_PATHS = {
    "scripts/cron/build-cron-identity-inventory.py",
    "scripts/cron/cron_identity.py",
    "scripts/cron/cron_render.py",
    "scripts/cron/cron_transaction.py",
    "scripts/cron/cron_line_model.py",
    "config/scheduled-tasks/schedule-tasks.yaml",
    "config/workstations/registry.yaml",
    "config/workstations/harness-state-classes.yaml",
    "docs/reports/issue-3475-command-identity-inventory.json",
}
SCHEDULER_PATHS = {
    "scripts/enforcement/check-scheduler-mutation-surfaces.py",
    "scripts/enforcement/scheduler_mutation_contract.py",
    "scripts/enforcement/scheduler_mutation_attestations.py",
    "scripts/enforcement/scheduler_mutation_python_flow.py",
    "scripts/enforcement/scheduler_mutation_discovery.py",
    "scripts/enforcement/scheduler_mutation_delegation.py",
    "scripts/enforcement/scheduler_mutation_report.py",
    "scripts/enforcement/scheduler_mutation_wrapper_attestations.py",
    "docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html",
} | INVENTORY_PATHS


class SnapshotError(RuntimeError):
    """The requested immutable tree cannot be validated safely."""


@dataclass(frozen=True)
class Entry:
    mode: str
    oid: str
    path: str


@dataclass(frozen=True)
class Snapshot:
    repo: Path
    tree_oid: str
    entries: dict[str, Entry]

    def read_blob(self, path: str) -> bytes:
        try:
            entry = self.entries[path]
        except KeyError as exc:
            raise SnapshotError(f"captured path is missing: {path}") from exc
        if entry.mode not in REGULAR_MODES:
            raise SnapshotError(f"captured path is not regular: {path}")
        body = _git(self.repo, "cat-file", "blob", entry.oid)
        actual = _git(self.repo, "hash-object", "--stdin", input_bytes=body).decode().strip()
        if actual != entry.oid:
            raise SnapshotError(f"captured blob hash mismatch: {path}")
        return body


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    try:
        result = subprocess.run(
            ["git", "--no-replace-objects", *args], cwd=repo,
            input=input_bytes, capture_output=True, check=False
        )
    except OSError as exc:
        raise SnapshotError(f"git transport failed: {args[0]}") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise SnapshotError(f"git {args[0]} failed: {detail}")
    return result.stdout


def _parse_frame(frame: bytes) -> Entry:
    try:
        metadata, raw_path = frame.split(b"\t", 1)
        mode, kind, raw_oid = metadata.split(b" ")
        path = raw_path.decode("utf-8", "strict")
        oid = raw_oid.decode("ascii", "strict")
        mode_text = mode.decode("ascii", "strict")
    except (UnicodeError, ValueError) as exc:
        raise SnapshotError("malformed ls-tree frame") from exc
    if kind not in {b"blob", b"commit"} or not re.fullmatch(r"[0-9]{6}", mode_text):
        raise SnapshotError(f"malformed tree entry: {path}")
    if not OID_RE.fullmatch(oid):
        raise SnapshotError(f"malformed tree entry OID: {path}")
    return Entry(mode_text, oid, path)


def capture_tree(repo: Path, tree_oid: str) -> Snapshot:
    repo = repo.resolve()
    if not OID_RE.fullmatch(tree_oid):
        raise SnapshotError("tree OID must be 40 or 64 lowercase hexadecimal characters")
    if _git(repo, "cat-file", "-t", tree_oid).strip() != b"tree":
        raise SnapshotError("captured OID is not a tree")
    raw = _git(repo, "ls-tree", "-rz", "--full-tree", tree_oid)
    if not raw or not raw.endswith(b"\0"):
        raise SnapshotError("tree manifest is empty or truncated")
    entries: dict[str, Entry] = {}
    for frame in raw[:-1].split(b"\0"):
        entry = _parse_frame(frame)
        if entry.path in entries:
            raise SnapshotError(f"duplicate tree path: {entry.path}")
        entries[entry.path] = entry
    return Snapshot(repo, tree_oid, entries)


def _path_key(path: str) -> str:
    return unicodedata.normalize("NFKC", path).casefold()


def _validate_component(component: str) -> None:
    if not component or component in {".", ".."} or component[-1:] in {".", " "}:
        raise SnapshotError(f"unsafe path component: {component!r}")
    stem = unicodedata.normalize("NFKC", component).split(".", 1)[0].upper()
    if stem in RESERVED:
        raise SnapshotError(f"Windows-reserved path component: {component}")
    if any(ord(character) < 32 or character in '<>:"|?*' for character in component):
        raise SnapshotError(f"Windows-forbidden path component: {component}")


def validate_materialization_entries(entries: list[Entry]) -> None:
    seen: dict[str, str] = {}
    for entry in entries:
        path = entry.path
        pure = PurePosixPath(path)
        if (
            entry.mode not in REGULAR_MODES
            or not path
            or "\\" in path
            or path.startswith("/")
            or path.startswith("//")
            or DRIVE_RE.match(path)
            or pure.is_absolute()
        ):
            raise SnapshotError(f"unsafe materialization entry: {path}")
        for component in pure.parts:
            _validate_component(component)
        key = _path_key(path)
        if key in seen and seen[key] != path:
            raise SnapshotError(f"case/Unicode path collision: {seen[key]} vs {path}")
        seen[key] = path
    keys = set(seen)
    for key in keys:
        parts = key.split("/")
        for length in range(1, len(parts)):
            parent = "/".join(parts[:length])
            if parent in keys:
                raise SnapshotError(f"file/directory path collision: {seen[parent]}")


def _destination(root: Path, path: str) -> Path:
    destination = root.joinpath(*PurePosixPath(path).parts)
    root_abs = os.path.abspath(root)
    dest_abs = os.path.abspath(destination)
    if os.path.commonpath([root_abs, dest_abs]) != root_abs:
        raise SnapshotError(f"materialization escaped root: {path}")
    return destination


def _materialize(snapshot: Snapshot, root: Path, paths: set[str]) -> None:
    missing = paths - snapshot.entries.keys()
    if missing:
        raise SnapshotError(f"captured closure is missing: {sorted(missing)!r}")
    selected = [snapshot.entries[path] for path in sorted(paths)]
    validate_materialization_entries(selected)
    destinations = [(entry, _destination(root, entry.path)) for entry in selected]
    for entry, destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(snapshot.read_blob(entry.path))
        if entry.mode == "100755" and os.name != "nt":
            destination.chmod(destination.stat().st_mode | stat.S_IXUSR)


def _sanitized_env() -> dict[str, str]:
    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith(("PYTHON", "UV_")) and key != "VIRTUAL_ENV"
    }
    env["PYTHONNOUSERSITE"] = "1"
    env["UV_NO_CONFIG"] = "1"
    return env


def verify_captured_context(root: Path) -> None:
    declared = os.environ.get("CAPTURED_TREE_OID", "")
    index = Path(os.environ.get("GIT_INDEX_FILE", ""))
    worktree = Path(os.environ.get("GIT_WORK_TREE", ""))
    if not OID_RE.fullmatch(declared):
        raise SnapshotError("captured-tree coordinator attestation is missing")
    resolved_root = root.resolve()
    if (
        not index.is_file()
        or index.resolve().parent != resolved_root
        or worktree.resolve() != resolved_root
    ):
        raise SnapshotError("captured-tree coordinator index is invalid")
    completed = subprocess.run(
        ["git", "--no-replace-objects", "write-tree"], cwd=root,
        text=True, capture_output=True,
    )
    if completed.returncode or completed.stdout.strip() != declared:
        raise SnapshotError("captured-tree coordinator index does not match declared tree")


def _frozen_git_env(snapshot: Snapshot, root: Path, index: Path) -> dict[str, str]:
    env = _sanitized_env()
    git_dir = _git(snapshot.repo, "rev-parse", "--absolute-git-dir").decode().strip()
    env.update({
        "GIT_DIR": git_dir,
        "GIT_WORK_TREE": str(root),
        "GIT_INDEX_FILE": str(index.resolve()),
        "GIT_NO_REPLACE_OBJECTS": "1",
        "CAPTURED_TREE_OID": snapshot.tree_oid,
    })
    manifest = bytearray()
    for entry in snapshot.entries.values():
        kind = "commit" if entry.mode == "160000" else "blob"
        manifest += f"{entry.mode} {kind} {entry.oid}\t{entry.path}".encode() + b"\0"
    result = subprocess.run(
        ["git", "--no-replace-objects", "update-index", "-z", "--index-info"],
        cwd=root, env=env, input=bytes(manifest), capture_output=True,
    )
    if result.returncode:
        raise SnapshotError("could not construct frozen captured index")
    return env


def _sync_environment(root: Path, env: dict[str, str]) -> Path:
    env["UV_PROJECT_ENVIRONMENT"] = str(root / ".venv")
    env["UV_CACHE_DIR"] = str(root / ".uv-cache")
    env["UV_PYTHON"] = sys.executable
    result = subprocess.run(
        ["uv", "sync", "--project", str(root), "--frozen", "--no-dev", "--no-install-project"],
        cwd=root, env=env, capture_output=True,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise SnapshotError(f"captured uv sync failed: {detail}")
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        raise SnapshotError("captured environment did not provide Python")
    return python


def _child_command(mode: str, python: Path) -> list[str]:
    if mode == "inventory":
        return [str(python), "-I", "scripts/cron/build-cron-identity-inventory.py",
                "--check", "--captured-tree"]
    command = [str(python), "-I", "scripts/enforcement/check-scheduler-mutation-surfaces.py",
               "--captured-tree"]
    if mode == "html":
        command += ["--check-html", "docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html"]
    return command


def _run_modes(snapshot: Snapshot, modes: list[str]) -> int:
    root = Path(tempfile.mkdtemp(prefix="git-index-snapshot-"))
    status = 0
    try:
        paths = COMMON_PATHS | INVENTORY_PATHS
        if any(mode in {"registry", "html"} for mode in modes):
            paths |= SCHEDULER_PATHS
        _materialize(snapshot, root, paths)
        env = _frozen_git_env(snapshot, root, root / ".captured-index")
        python = _sync_environment(root, env)
        for mode in modes:
            result = subprocess.run(_child_command(mode, python), cwd=root, env=env)
            status |= int(result.returncode != 0)
    finally:
        try:
            shutil.rmtree(root)
        except OSError as exc:
            if status == 0:
                raise SnapshotError(f"snapshot cleanup failed: {exc}") from exc
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-oid", required=True)
    parser.add_argument("mode", choices=("all", "registry", "inventory", "html"))
    args = parser.parse_args(argv)
    try:
        repo = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        snapshot = capture_tree(repo, args.tree_oid)
        modes = ["registry", "inventory", "html"] if args.mode == "all" else [args.mode]
        return _run_modes(snapshot, modes)
    except SnapshotError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
