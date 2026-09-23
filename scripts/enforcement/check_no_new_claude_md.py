#!/usr/bin/env python3
"""Reject new or changed active CLAUDE.md files against a pinned inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
from typing import Any


EXCLUDED_COMPONENTS = frozenset({"archive", "_archive", "vendor", "vendors"})
EXCLUDED_PREFIXES = (
    ("tests", "fixtures"),
    (".agents", "skills", "creative", "popular-web-designs", "templates"),
    (".claude", "skills", "creative", "popular-web-designs", "templates"),
)


class GateError(Exception):
    """An input or filesystem ambiguity that must fail closed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_root(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=True)))


def excluded(path: str) -> bool:
    parts = tuple(part.lower() for part in PurePosixPath(path).parts)
    return any(part in EXCLUDED_COMPONENTS for part in parts) or any(
        parts[: len(prefix)] == prefix for prefix in EXCLUDED_PREFIXES
    )


def safe_relative(value: str) -> str:
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        not value
        or "\\" in value
        or posix.is_absolute()
        or windows.drive
        or windows.root
        or any(part in {".", ".."} for part in posix.parts)
    ):
        raise GateError(f"unsafe baseline path: {value}")
    return posix.as_posix()


def load_baseline(path: Path, expected_digest: str, repo_root: Path) -> dict[str, str]:
    if not path.is_file() or path.is_symlink():
        raise GateError("baseline must be a regular non-symlink file")
    raw = path.read_bytes()
    if sha256_bytes(raw) != expected_digest.lower():
        raise GateError("baseline digest mismatch")
    try:
        payload: Any = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError(f"invalid baseline JSON: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("repositories"), list):
        raise GateError("baseline repositories list missing")

    matches = [
        item
        for item in payload["repositories"]
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and os.path.normcase(str(Path(item["path"]).resolve())) == normalized_root(repo_root)
    ]
    if len(matches) != 1:
        raise GateError("repository root mismatch or duplicate baseline entry")

    result: dict[str, str] = {}
    files = matches[0].get("tracked_instruction_files")
    if not isinstance(files, list):
        raise GateError("tracked_instruction_files list missing")
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise GateError("invalid tracked instruction record")
        relative = safe_relative(item["path"])
        if PurePosixPath(relative).name.lower() != "claude.md" or excluded(relative):
            continue
        working = item.get("working")
        digest = working.get("content_sha256") if isinstance(working, dict) else None
        if not isinstance(digest, str) or len(digest) != 64:
            raise GateError(f"baseline working digest missing: {relative}")
        if relative in result:
            raise GateError(f"duplicate baseline path: {relative}")
        result[relative] = digest.lower()
    return result


def git_candidates(repo_root: Path) -> list[str]:
    outputs: list[bytes] = []
    clean_env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    for arguments in (
        ["--cached", "--others", "--exclude-standard"],
        ["--others", "--ignored", "--exclude-standard"],
    ):
        result = subprocess.run(
            ["git", "ls-files", "-z", *arguments],
            cwd=repo_root,
            env=clean_env,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise GateError("git ls-files failed")
        outputs.extend(result.stdout.split(b"\0"))
    return sorted(
        {
        PurePosixPath(os.fsdecode(raw)).as_posix()
        for raw in outputs
        if raw and PurePosixPath(os.fsdecode(raw)).name.lower() == "claude.md"
        }
    )


def observed_digest(repo_root: Path, relative: str) -> str:
    parts = PurePosixPath(relative).parts
    parent = repo_root
    for part in parts[:-1]:
        parent /= part
        try:
            parent_stat = parent.lstat()
        except FileNotFoundError as exc:
            raise GateError(f"baseline CLAUDE.md parent is missing: {relative}") from exc
        parent_reparse = getattr(parent_stat, "st_file_attributes", 0) & 0x400
        if parent.is_symlink() or parent_reparse:
            raise GateError(f"linked ancestor is ambiguous: {relative}")
    path = parent / parts[-1]
    if path.is_symlink():
        raise GateError(f"symlink CLAUDE.md is ambiguous: {relative}")
    try:
        resolved = path.resolve(strict=True)
        stat_result = path.stat()
    except FileNotFoundError as exc:
        raise GateError(f"baseline CLAUDE.md is missing: {relative}") from exc
    reparse_flag = getattr(stat_result, "st_file_attributes", 0) & 0x400
    if reparse_flag or not path.is_file():
        raise GateError(f"non-regular CLAUDE.md is ambiguous: {relative}")
    if not resolved.is_relative_to(repo_root):
        raise GateError(f"CLAUDE.md escapes repo root: {relative}")
    return sha256_bytes(path.read_bytes())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--baseline-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.repo_root.resolve(strict=True)
        if not (root / ".git").exists():
            raise GateError("repo root has no .git entry")
        baseline = load_baseline(args.baseline, args.baseline_sha256, root)
        candidates = git_candidates(root)
        active = [path for path in candidates if not excluded(path)]
        excluded_count = len(candidates) - len(active)
        new = sorted(set(active) - set(baseline))
        changed: list[str] = []
        for relative, expected in sorted(baseline.items()):
            actual = observed_digest(root, relative)
            if actual != expected:
                changed.append(relative)
            else:
                print(f"BASELINE {relative}")
        for relative in new:
            observed_digest(root, relative)
            print(f"NEW {relative}")
        for relative in changed:
            print(f"CHANGED {relative}")
        if new or changed:
            print(f"FAIL baseline={len(baseline)} new={len(new)} changed={len(changed)}")
            return 1
        print(
            f"PASS baseline={len(baseline)} new=0 changed=0 excluded={excluded_count}"
        )
        return 0
    except (GateError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
