#!/usr/bin/env python3
"""audit-word-count.py — Measure SKILL.md sizes and flag oversized skills.

Finds all SKILL.md files under .claude/skills/ (excluding _archive/),
counts words and lines in the body (after frontmatter), and classifies
violations by severity.

Usage:
    uv run --no-project python scripts/skills/audit-word-count.py
"""
import os
import re
import sys
from pathlib import Path


def find_skill_files(root: Path) -> list[Path]:
    """Walk .claude/skills/ for SKILL.md, skipping _archive/."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune _archive directories
        dirnames[:] = [d for d in dirnames if d != "_archive"]
        if "SKILL.md" in filenames:
            results.append(Path(dirpath) / "SKILL.md")
    return sorted(results)


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- ... ---) and return the body."""
    m = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.DOTALL)
    if m:
        return text[m.end():]
    return text


def classify(lines: int, words: int) -> list[str]:
    """Return list of violation tags."""
    tags = []
    if lines > 500:
        tags.append("CRITICAL")
    elif lines > 200:
        tags.append("WARNING")
    if words > 500:
        tags.append("OVER_BUDGET")
    return tags


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    skills_root = repo_root / ".claude" / "skills"

    if not skills_root.is_dir():
        print(f"ERROR: {skills_root} not found", file=sys.stderr)
        return 1

    files = find_skill_files(skills_root)
    print(f"Scanned {len(files)} SKILL.md files\n")

    # Counters
    critical = []
    warning = []
    over_budget = []
    clean = []

    print(f"{'Lines':>6}  {'Words':>6}  {'Status':<15}  Path")
    print("-" * 80)

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        body = strip_frontmatter(text)
        lines = body.count("\n") + (1 if body and not body.endswith("\n") else 0)
        words = len(body.split())
        tags = classify(lines, words)

        rel = path.relative_to(repo_root)

        if not tags:
            status = "OK"
            clean.append((rel, lines, words))
        else:
            status = ",".join(tags)

        if "CRITICAL" in tags:
            critical.append((rel, lines, words))
        if "WARNING" in tags:
            warning.append((rel, lines, words))
        if "OVER_BUDGET" in tags:
            over_budget.append((rel, lines, words))

        # Only print non-OK or print all if verbose
        if tags:
            print(f"{lines:>6}  {words:>6}  {status:<15}  {rel}")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Total skills scanned:  {len(files)}")
    print(f"  CRITICAL (>500 lines): {len(critical)}")
    print(f"  WARNING  (>200 lines): {len(warning)}")
    print(f"  OVER_BUDGET (>500 w):  {len(over_budget)}")
    print(f"  Clean:                 {len(clean)}")
    print()

    if critical:
        print("CRITICAL files:")
        for rel, lines, words in critical:
            print(f"  {lines:>5}L {words:>5}w  {rel}")

    if warning:
        print("WARNING files:")
        for rel, lines, words in warning:
            print(f"  {lines:>5}L {words:>5}w  {rel}")

    if over_budget:
        print("OVER_BUDGET files:")
        for rel, lines, words in over_budget:
            print(f"  {lines:>5}L {words:>5}w  {rel}")

    # Exit 1 if any violations
    return 1 if (critical or warning or over_budget) else 0


if __name__ == "__main__":
    sys.exit(main())
