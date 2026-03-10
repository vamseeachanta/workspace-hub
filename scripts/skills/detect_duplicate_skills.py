#!/usr/bin/env python3
"""detect_duplicate_skills.py — Scan all SKILL.md files for duplicate `name:` values.

Prints WARNING for any duplicates. Always exits 0 (non-blocking).
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect duplicate skill names")
    parser.add_argument(
        "--skills-dir",
        default=".claude/skills",
        help="Root directory to scan for SKILL.md files (default: .claude/skills)",
    )
    return parser.parse_args()


def extract_name(skill_md: Path) -> str | None:
    """Extract `name:` from YAML frontmatter, case-insensitive trimmed."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    if not text.startswith("---"):
        return skill_md.parent.name  # fallback to directory name

    end = text.find("\n---", 3)
    fm = text[4:end] if end != -1 else text[4:]

    for line in fm.splitlines():
        if line.strip().lower().startswith("name:"):
            _, _, val = line.partition(":")
            return val.strip().strip("'\"").lower()

    return skill_md.parent.name.lower()


def find_skill_files(skills_dir: Path) -> list[Path]:
    """Walk skills directory using os.walk for better performance on slow filesystems."""
    import os
    results = []
    for root, dirs, files in os.walk(str(skills_dir)):
        root_path = Path(root)
        # Skip archive/diverged dirs — modify dirs in-place to prune traversal
        dirs[:] = [
            d for d in dirs
            if d not in ("_archive", "_diverged")
        ]
        if "SKILL.md" in files:
            results.append(root_path / "SKILL.md")
    return sorted(results)


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    skills_dir = repo_root / args.skills_dir

    if not skills_dir.exists():
        print(f"WARNING: skills directory not found: {skills_dir}", file=sys.stderr)
        return 0

    name_to_paths: dict[str, list[str]] = defaultdict(list)

    for skill_md in find_skill_files(skills_dir):
        name = extract_name(skill_md)
        if name:
            rel = str(skill_md.relative_to(repo_root))
            name_to_paths[name].append(rel)

    total = sum(len(v) for v in name_to_paths.values())
    print(f"Scanned {total} SKILL.md files across {len(name_to_paths)} unique names")

    duplicates = {name: paths for name, paths in name_to_paths.items() if len(paths) > 1}
    if not duplicates:
        print("No duplicate skill names found.")
        return 0

    for name, paths in sorted(duplicates.items()):
        path_list = ", ".join(paths)
        print(f"WARNING: DUPLICATE skill name '{name}': {path_list}")

    print(f"\n{len(duplicates)} duplicate name(s) found across {total} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
