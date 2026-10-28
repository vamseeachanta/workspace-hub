#!/usr/bin/env python3
"""Measure family collection, with import-time effects confined to scratch.

Collection imports Python code. The probe is a diagnostic guard, not an OS
sandbox: external processes, network access, solver imports and writes outside
scratch are refused. Raw diagnostics stay in scratch; public errors are reduced
to exception classes and missing Python dependency names.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()


def cached_result(path: Path, digest: str) -> dict | None:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("digest") == digest:
            return data
    return None


def body_status(family: str, policy: dict) -> str:
    return "EVALUATED" if family in policy["body_evaluated"] else "NOT_EVALUATED"


def public_error(text: str) -> str:
    """Do not copy arbitrary exception values or traceback source into reports."""
    missing = sorted(set(re.findall(r"ModuleNotFoundError: No module named '([a-zA-Z_][a-zA-Z0-9_.]*)'", text)))
    kinds = sorted(set(re.findall(r"\b([A-Z][a-zA-Z]*(?:Error|Exception))\b", text)))
    messages = [f"ModuleNotFoundError: No module named '{name}'" for name in missing]
    messages.extend(kind for kind in kinds if kind != "ModuleNotFoundError")
    if "collection guard" in text:
        messages.append("collection guard denied an import-time effect")
    return "; ".join(messages) or "collection failed; raw diagnostics retained in scratch"


def install_guard(scratch: Path) -> None:
    def permitted(path) -> bool:
        if isinstance(path, int):
            return True
        return Path(os.fsdecode(path)).resolve().is_relative_to(scratch)

    def audit(event, args):
        if event == "import" and args[0].split(".")[0].lower() in {
            "orcfxapi", "orcaflex", "orcawave", "aqwa", "ansys",
        }:
            raise PermissionError("collection guard denied external solver import")
        if (event.startswith(("subprocess.", "os.exec", "os.spawn", "os.posix_spawn", "os.fork"))
                or event in {"os.system", "socket.connect", "socket.bind", "socket.getaddrinfo"}):
            raise PermissionError("collection guard denied external operation")
        if event == "open":
            _, mode, flags = args
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+"))
            writing = writing or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing and not permitted(args[0]):
                raise PermissionError("collection guard denied write outside scratch")
        if event in {"os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.truncate",
                     "os.rename", "os.link", "os.symlink"}:
            paths = args[:2] if event in {"os.rename", "os.link", "os.symlink"} else args[:1]
            if not all(permitted(path) for path in paths):
                raise PermissionError("collection guard denied mutation outside scratch")

    sys.addaudithook(audit)


def probe(root: Path, scratch: Path, result_path: Path, files: list[str]) -> int:
    os.chdir(root)
    sys.path[:0] = [str(root), str(root / "src"), str(root / "scripts")]
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["TMPDIR"] = str(scratch)
    tempfile.tempdir = str(scratch)
    sys.dont_write_bytecode = True
    install_guard(scratch.resolve())
    import pytest

    class Recorder:
        collected = 0
        errors: ClassVar[list[str]] = []

        def pytest_collection_finish(self, session):
            self.collected = len(session.items)

        def pytest_collectreport(self, report):
            if report.failed:
                self.errors.append(public_error(str(report.longrepr)))

    recorder = Recorder()
    # Source: pytest usage documentation, --collect-only (accessed 2026-10-22).
    rc = pytest.main(["--collect-only", "-q", "-p", "no:cacheprovider",
                      "--log-file", str(scratch / "pytest.log"),
                      "--basetemp", str(scratch / "pytest"), "--", *files], plugins=[recorder])
    data = {"collected": recorder.collected,
            "collection_status": "COLLECTABLE" if rc == 0 and recorder.collected else "NOT_GATING",
            "error": "; ".join(sorted(set(recorder.errors))) if rc else ""}
    if data["collection_status"] == "NOT_GATING" and not data["error"]:
        data["error"] = "no tests collected" if not recorder.collected else "collection command failed"
    result_path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


def collect_family(root: Path, files: list[str], scratch: Path, timeout: float,
                   runner=subprocess.run) -> dict:
    scratch.mkdir(parents=True, exist_ok=True)
    result_path = scratch / "result.json"
    env = {key: value for key, value in os.environ.items()
           if key in {"PATH", "LANG", "LC_ALL", "TMPDIR", "PYTHONDONTWRITEBYTECODE", "UV_CACHE_DIR"}}
    env.update({"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "MARKDOWN_QA_ARTIFACTS_DIR": str(scratch / "markdown-artifacts"),
                "MARKDOWN_QA_SESSIONFINISH_SENTINEL": str(scratch / "markdown-sentinel")})
    try:
        with (scratch / "collection.log").open("w", encoding="utf-8", newline="\n") as log:
            result = runner([sys.executable, "-I", str(SCRIPT), "probe", "--root", str(root),
                             "--scratch", str(scratch), "--result", str(result_path),
                             "--files", *files], cwd=root, env=env, stdout=log,
                            stderr=subprocess.STDOUT, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"collected": None, "collection_status": "NOT_GATING", "error": "collection timeout"}
    if result.returncode or not result_path.exists():
        return {"collected": None, "collection_status": "NOT_GATING",
                "error": public_error((scratch / "collection.log").read_text(encoding="utf-8"))}
    return json.loads(result_path.read_text(encoding="utf-8"))


def is_link(path: Path) -> bool:
    """Exclude symlinks and Windows reparse points, including junctions."""
    return path.is_symlink() or bool(
        getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def input_digest(root: Path, inventory: dict, policy: dict, timeout: float) -> str:
    """Resume only when source, test, configuration and interpreter inputs agree."""
    digest = hashlib.sha256(json.dumps([inventory, policy, timeout, sys.version], sort_keys=True).encode())
    # Hash potential local imports, not just test modules. Symlink targets are not followed.
    paths = set()
    for directory in ("scripts", "src", "tests", "coordination", "config"):
        target = root / directory
        if not target.exists() or is_link(target):
            continue
        for parent, dirs, files in os.walk(target, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in {".venv", "__pycache__", ".git"}
                             and not is_link(Path(parent) / d))
            paths.update(Path(parent) / f for f in files
                         if not is_link(Path(parent) / f)
                         and (Path(parent) / f).relative_to(root).as_posix()
                         != "config/ci/hub-test-health.json")
    paths.update(path for path in (root / "pyproject.toml", root / "pytest.ini") if path.exists())
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    import pytest
    digest.update(pytest.__version__.encode())
    digest.update(json.dumps(environment_versions(), sort_keys=True).encode())
    return digest.hexdigest()


def environment_versions() -> dict:
    return {"python": sys.version.split()[0],
            "packages": dict(sorted((dist.metadata["Name"], dist.version)
                                    for dist in importlib.metadata.distributions()
                                    if dist.metadata["Name"]))}


def render(data: dict, policy: dict) -> str:
    rows = ["# Hub test family collection health", "",
            "Collection is diagnostic. Successful collection does not qualify test-body effects.", "",
            "## Revision history", "", "| Revision | Date | Change and reason |",
            "|---|---|---|", "| 1 | 2026-10-22 | Establish advisory family collection coverage. |", "",
            "Generated by `scripts/ci/hub_test_health.py`; raw diagnostics remain in scratch.",
            "Exception values are omitted except missing Python dependency names.",
            f"Collection timeout input: {data['timeout_seconds']:g} seconds per family.",
            f"Interpreter: Python {data['environment']['python']}; "
            + ", ".join(f"{name} {version}" for name, version in data['environment']['packages'].items()) + ".",
            "No test bodies were run by the collection command. No licensed solver was imported or queried.",
            "Autoloaded third-party plugins are disabled for reproducible diagnostics; local conftests run.",
            "The import-time guard may reject effects that a normal pytest run permits.", "",
            "Body policy: " + policy["not_evaluated_reason"], "",
            "| Family | Files | Collected | Collection | Bodies | Error |",
            "|---|---:|---:|---|---|---|"]
    for name, row in sorted(data["families"].items()):
        count = row["collected"] if row["collected"] is not None else "unknown"
        error = row["error"].replace("|", "\\|").replace("\n", " ") or "none"
        rows.append(f"| `{name}` | {row['file_count']} | {count} | {row['collection_status']} | {row['body_status']} | {error} |")
    rows.extend(["", "EVALUATED identifies the synthetic CI harness policy, not a result of running bodies here.",
                 "NOT_GATING excludes collection failures; NOT_EVALUATED excludes unreviewed bodies.", ""])
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    p.add_argument("--result", type=Path, required=True)
    p.add_argument("--files", nargs="+", required=True)
    p = sub.add_parser("generate")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--scratch", type=Path, required=True)
    p.add_argument("--timeout-seconds", type=float, required=True)
    args = parser.parse_args()
    if args.command == "probe":
        return probe(args.root.resolve(), args.scratch.resolve(), args.result.resolve(), args.files)
    if args.timeout_seconds <= 0:
        parser.error("Timeout must be positive")
    root, scratch = args.root.resolve(), args.scratch.resolve()
    if scratch.is_relative_to(root):
        parser.error("Scratch must be outside the repository")
    scratch.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((root / "config/ci/hub-test-families.json").read_text(encoding="utf-8"))
    policy = json.loads((root / "config/ci/hub-test-policy.json").read_text(encoding="utf-8"))
    digest = input_digest(root, inventory, policy, args.timeout_seconds)
    results = {}
    for family, files in sorted(inventory["families"].items()):
        case = scratch / hashlib.sha256(family.encode()).hexdigest()
        cache = case / "cache.json"
        row = cached_result(cache, digest)
        if row is None:
            row = collect_family(root, files, case, args.timeout_seconds)
            row.update({"digest": digest, "file_count": len(files),
                        "body_status": body_status(family, policy)})
            cache.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        results[family] = row
        print(f"{family}: {row['collection_status']} ({row['collected']})", flush=True)
    data = {"timeout_seconds": args.timeout_seconds, "environment": environment_versions(),
            "families": results}
    (root / "config/ci/hub-test-health.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    target = root / "docs/ci/hub-test-family-health.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(data, policy), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
