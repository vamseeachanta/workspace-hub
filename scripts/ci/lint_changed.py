#!/usr/bin/env python3
"""Lint the Python files a pull request changes; fail only on new findings.

Rules are ruff's fatal set (syntax errors, invalid comparisons, misplaced
statements, undefined names). Ruff runs with ``--isolated`` because nested
example ``pyproject.toml`` files in the tree are not lint configuration.
Findings already present in the base version of a file are reported but do not
fail the gate, so touching an old file does not inherit its debt.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = "E9,F63,F7,F82"


def git(root: Path, *args: str) -> bytes:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, check=True).stdout


def changed_python(root: Path, base: str, head: str) -> list[str]:
    out = git(root, "diff", "--name-only", "-z", "--diff-filter=ACMR", "--end-of-options",
              f"{base}...{head}", "--", "*.py")
    return sorted(p for p in out.decode().split("\0") if p)


def ruff(directory: Path, files: list[str]) -> list[dict]:
    if not files:
        return []
    exe = shutil.which("ruff")
    cmd = [exe] if exe else [sys.executable, "-m", "ruff"]
    result = subprocess.run([*cmd, "check", "--isolated", "--select", RULES, "--output-format",
                             "json", "--exit-zero", "--", *files],
                            cwd=directory, capture_output=True, text=True, check=True)
    rows = json.loads(result.stdout or "[]")
    for row in rows:
        row["filename"] = Path(row["filename"]).resolve().relative_to(directory.resolve()).as_posix()
    return rows


def key(row: dict) -> tuple[str, str, str]:
    return row["filename"], row.get("code") or "syntax-error", row["message"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    files = [f for f in changed_python(root, args.base, args.head) if (root / f).is_file()]
    print(f"Changed Python files: {len(files)}")
    head_rows = ruff(root, files)
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        base_files = []
        merge_base = git(root, "merge-base", args.base, args.head).decode().strip()
        for name in files:
            try:
                blob = git(root, "show", f"{merge_base}:{name}")
            except subprocess.CalledProcessError:
                continue  # new file: every finding is new
            target = base_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            base_files.append(name)
        base_rows = ruff(base_dir, base_files)
    allowance = Counter(key(r) for r in base_rows)
    new = []
    for row in head_rows:
        k = key(row)
        if allowance[k]:
            allowance[k] -= 1
        else:
            new.append(row)
    for row in head_rows:
        level = "error" if row in new else "warning"
        loc = row.get("location") or {}
        print(f"::{level} file={row['filename']},line={loc.get('row', 1)}::"
              f"{row.get('code') or 'syntax-error'} {row['message']}")
    print(f"Findings: {len(head_rows)} total, {len(new)} new (rules {RULES})")
    return 1 if new else 0


if __name__ == "__main__":
    raise SystemExit(main())
