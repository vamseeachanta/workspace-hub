#!/usr/bin/env python3
"""Reject newly added/copied/renamed files under retired local queue paths."""

from __future__ import annotations

import argparse
import subprocess
import sys

RETIRED_PREFIXES = (".claude/work-queue/", ".planning/")
ARCHIVE_PREFIXES = (
    ".claude/work-queue/_archive/",
    ".planning/archive/",
)


def changed_paths(base_ref: str, head_ref: str) -> list[tuple[str, str]]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACR",
            base_ref,
            head_ref,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [("A", line) for line in result.stdout.splitlines() if line]


def is_allowed_retired_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if not normalized.startswith(RETIRED_PREFIXES):
        return True
    return normalized.startswith(ARCHIVE_PREFIXES)


def violations(rows: list[tuple[str, str]]) -> list[str]:
    blocked: list[str] = []
    for status, path in rows:
        if not status.startswith(("A", "C", "R")):
            continue
        if not is_allowed_retired_path(path):
            blocked.append(path)
    return blocked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--path", action="append", default=[])
    args = parser.parse_args()

    rows = [("A", p) for p in args.path] if args.path else changed_paths(
        args.base_ref,
        args.head_ref,
    )
    blocked = violations(rows)
    if blocked:
        print("New files under retired local queue paths are blocked:", file=sys.stderr)
        for path in blocked:
            print(f"- {path}", file=sys.stderr)
        return 1
    print("OK: no new retired local queue files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
