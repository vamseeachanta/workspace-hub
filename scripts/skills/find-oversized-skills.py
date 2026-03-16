#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Find SKILL.md files exceeding a line count threshold.

Usage:
    uv run --no-project python scripts/skills/find-oversized-skills.py
    uv run --no-project python scripts/skills/find-oversized-skills.py --min-lines 400
    uv run --no-project python scripts/skills/find-oversized-skills.py --root .claude/skills
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_ROOT = Path(".claude/skills")
DEFAULT_MIN_LINES = 200


def find_oversized(root: Path, min_lines: int) -> list[tuple[int, Path]]:
    """Find SKILL.md files with more than min_lines lines.

    Returns list of (line_count, path) sorted descending by count.
    """
    results: list[tuple[int, Path]] = []
    for skill_path in sorted(root.rglob("SKILL.md")):
        try:
            line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if line_count > min_lines:
            results.append((line_count, skill_path))
    results.sort(key=lambda x: -x[0])
    return results


def infer_category(path: Path, root: Path) -> str:
    """Extract top-level category from path relative to root."""
    try:
        rel = path.relative_to(root)
        return rel.parts[0] if rel.parts else "unknown"
    except ValueError:
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Find oversized SKILL.md files")
    parser.add_argument("--root", default=str(DEFAULT_ROOT),
                        help="Root directory to search")
    parser.add_argument("--min-lines", type=int, default=DEFAULT_MIN_LINES,
                        help="Minimum line count to report")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        return 2

    results = find_oversized(root, args.min_lines)
    for count, path in results:
        category = infer_category(path, root)
        print(f"{count:6d}  {category:20s}  {path}")

    print(f"\n{len(results)} skills over {args.min_lines} lines", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
