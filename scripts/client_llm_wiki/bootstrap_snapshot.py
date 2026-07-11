"""Immutable, replacement-free snapshots of committed template objects."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

from .bootstrap_git import isolated_env


class BootstrapSnapshotError(RuntimeError):
    """Committed template objects violate the closed snapshot contract."""


@dataclass(frozen=True, slots=True)
class TemplateMember:
    path: str
    data: bytes | None
    mode: int
    object_oid: str

    @property
    def is_directory(self) -> bool:
        return self.data is None


@dataclass(frozen=True, slots=True)
class TemplateSnapshot:
    commit_oid: str
    tree_oid: str
    members: tuple[TemplateMember, ...]


_OID = re.compile(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_TREE_OUTPUT_LIMIT = 4 * 1024 * 1024
_BLOB_LIMIT = 16 * 1024 * 1024
_TOTAL_BLOB_LIMIT = 64 * 1024 * 1024
_GIT_TIMEOUT = 5
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _read_bounded(stream, limit: int, label: str) -> bytes:
    size = os.fstat(stream.fileno()).st_size
    if size > limit:
        raise BootstrapSnapshotError(f"Git {label} output exceeds size limit")
    stream.seek(0)
    return stream.read(limit + 1)


def _run_git(repo_fd: int, args: tuple[str, ...], limit: int) -> bytes:
    command = ["git", "-C", f"/proc/self/fd/{repo_fd}", *args]
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(
                command, check=False, stdout=stdout, stderr=stderr,
                pass_fds=(repo_fd,), env=isolated_env(), timeout=_GIT_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            raise BootstrapSnapshotError("Git snapshot command timed out") from exc
        error = _read_bounded(stderr, _TREE_OUTPUT_LIMIT, "error")
        if result.returncode != 0:
            detail = error.decode("utf-8", errors="replace").strip()
            raise BootstrapSnapshotError(f"Git snapshot command failed: {detail}")
        return _read_bounded(stdout, limit, "snapshot")


def _object_id(raw: bytes, label: str) -> str:
    value = raw.rstrip(b"\n")
    if not _OID.fullmatch(value):
        raise BootstrapSnapshotError(f"Git returned invalid {label} object ID")
    return value.decode("ascii")


def _safe_name(raw: bytes) -> str:
    try:
        name = raw.decode("utf-8")
    except UnicodeError as exc:
        raise BootstrapSnapshotError("template tree contains a non-UTF-8 path") from exc
    path = PurePosixPath(name)
    if not name or name in {".", "..", ".git"} or "/" in name or "\\" in name:
        raise BootstrapSnapshotError(f"unsafe template path component: {name!r}")
    if str(path) != name:
        raise BootstrapSnapshotError(f"invalid template path component: {name!r}")
    return name


def _decode_header(raw: bytes, label: str) -> str:
    try:
        return raw.decode("ascii")
    except UnicodeError as exc:
        raise BootstrapSnapshotError(f"Git tree contains invalid {label}") from exc


def _tree_entries(
    repo_fd: int, tree_oid: str,
) -> tuple[tuple[str, str, str, str], ...]:
    raw = _run_git(repo_fd, ("ls-tree", "-z", tree_oid), _TREE_OUTPUT_LIMIT)
    entries: list[tuple[str, str, str, str]] = []
    names: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_name = record.split(b"\t", 1)
            mode, kind, raw_oid = header.split(b" ", 2)
        except ValueError as exc:
            raise BootstrapSnapshotError("malformed Git tree record") from exc
        name = _safe_name(raw_name)
        if name in names:
            raise BootstrapSnapshotError(f"duplicate template tree entry: {name}")
        names.add(name)
        oid = _object_id(raw_oid, "tree entry")
        entries.append(
            (_decode_header(mode, "mode"), _decode_header(kind, "type"), oid, name)
        )
    return tuple(entries)


def _read_blob(repo_fd: int, oid: str) -> bytes:
    raw_size = _run_git(repo_fd, ("cat-file", "-s", oid), 64).rstrip(b"\n")
    if not raw_size.isdigit() or int(raw_size) > _BLOB_LIMIT:
        raise BootstrapSnapshotError("template blob has invalid or excessive size")
    data = _run_git(repo_fd, ("cat-file", "blob", oid), _BLOB_LIMIT)
    if len(data) != int(raw_size):
        raise BootstrapSnapshotError("template blob size changed while reading")
    return data


def _walk_tree(repo_fd: int, tree_oid: str) -> tuple[TemplateMember, ...]:
    members: list[TemplateMember] = []
    seen: set[str] = set()

    def walk(current_oid: str, prefix: str = "") -> None:
        for mode, kind, oid, name in _tree_entries(repo_fd, current_oid):
            path = f"{prefix}/{name}" if prefix else name
            if path in seen:
                raise BootstrapSnapshotError(f"duplicate template path: {path}")
            seen.add(path)
            if (mode, kind) == ("040000", "tree"):
                members.append(TemplateMember(path, None, 0o755, oid))
                walk(oid, path)
            elif kind == "blob" and mode in {"100644", "100755"}:
                data = _read_blob(repo_fd, oid)
                members.append(TemplateMember(path, data, int(mode[-3:], 8), oid))
            else:
                raise BootstrapSnapshotError(f"unsupported Git entry mode/type: {mode} {kind}")

    walk(tree_oid)
    if sum(len(member.data or b"") for member in members) > _TOTAL_BLOB_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds total size limit")
    return tuple(members)


def load_committed_snapshot(template_worktree: Path) -> TemplateSnapshot:
    """Pin HEAD and return exact committed template tree/blob contents."""
    repo_fd = -1
    try:
        repo_fd = os.open(Path(template_worktree), _DIR_FLAGS)
        commit = _object_id(
            _run_git(repo_fd, ("rev-parse", "HEAD^{commit}"), 128), "commit",
        )
        tree = _object_id(
            _run_git(
                repo_fd, ("rev-parse", f"{commit}:templates/client-llm-wiki"), 128,
            ),
            "template tree",
        )
        members = _walk_tree(repo_fd, tree)
        if not members:
            raise BootstrapSnapshotError("committed template is empty")
        return TemplateSnapshot(commit, tree, members)
    except OSError as exc:
        raise BootstrapSnapshotError(f"template worktree bind failed: {exc}") from exc
    finally:
        if repo_fd >= 0:
            os.close(repo_fd)
