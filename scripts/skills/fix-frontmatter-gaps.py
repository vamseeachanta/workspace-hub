#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Fix frontmatter gaps in SKILL.md files.

Adds missing category (from directory path) and version (1.0.0)
fields. Reports short descriptions for manual review.

Usage:
    uv run --no-project python scripts/skills/fix-frontmatter-gaps.py
    uv run --no-project python scripts/skills/fix-frontmatter-gaps.py --apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

DESC_MIN_WORDS = 10
DEFAULT_VERSION = "1.0.0"
SKILLS_ROOT = Path(".claude/skills")


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and body from content."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return None, content
    end = stripped.find("---", 3)
    if end == -1:
        return None, content
    raw = stripped[3:end].strip()
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, content
    if not isinstance(meta, dict):
        return None, content
    return meta, stripped[end + 3:]


def category_from_path(path: Path, root: Path) -> str:
    """Derive top-level category from directory path."""
    try:
        rel = path.relative_to(root)
        return rel.parts[0] if rel.parts else "unknown"
    except ValueError:
        return "unknown"


def add_missing_field(content: str, field: str, value: str) -> str:
    """Insert a field before the closing --- if not present."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return content
    end = stripped.find("---", 3)
    if end == -1:
        return content

    fm_text = stripped[3:end]
    if re.search(rf"^{re.escape(field)}\s*:", fm_text, re.MULTILINE):
        return content  # already present

    new_fm = fm_text.rstrip() + f"\n{field}: {value}\n"
    return "---\n" + new_fm + "---" + stripped[end + 3:]


def scan_gaps(skills_root: Path) -> list[dict]:
    """Scan all SKILL.md files and return gap records."""
    gaps: list[dict] = []
    for path in sorted(skills_root.rglob("SKILL.md")):
        content = path.read_text(encoding="utf-8", errors="replace")
        meta, _ = parse_frontmatter(content)
        if meta is None:
            continue

        name = meta.get("name", path.parent.name)
        missing: list[str] = []
        short = False

        if not meta.get("category"):
            missing.append("category")
        if not meta.get("version"):
            missing.append("version")

        desc = str(meta.get("description", ""))
        if desc and len(desc.split()) < DESC_MIN_WORDS:
            short = True

        if missing or short:
            cat = category_from_path(path, skills_root)
            gaps.append({
                "path": path,
                "name": name,
                "missing": missing,
                "short_description": short,
                "desc_words": len(desc.split()) if desc else 0,
                "desc_text": desc,
                "inferred_category": cat,
            })
    return gaps


def apply_fixes(
    skills_root: Path, *, dry_run: bool = True
) -> dict:
    """Fix category/version gaps. Return summary report."""
    gaps = scan_gaps(skills_root)
    report = {
        "category_fixed": 0,
        "version_fixed": 0,
        "short_descriptions": [],
        "dry_run": dry_run,
    }

    for gap in gaps:
        path: Path = gap["path"]
        content = path.read_text(encoding="utf-8", errors="replace")

        if "category" in gap["missing"]:
            content = add_missing_field(
                content, "category", gap["inferred_category"]
            )
            report["category_fixed"] += 1

        if "version" in gap["missing"]:
            content = add_missing_field(
                content, "version", DEFAULT_VERSION
            )
            report["version_fixed"] += 1

        if gap["short_description"]:
            report["short_descriptions"].append({
                "name": gap["name"],
                "path": str(gap["path"]),
                "words": gap["desc_words"],
                "current": gap["desc_text"],
            })

        if not dry_run and gap["missing"]:
            path.write_text(content, encoding="utf-8")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix frontmatter gaps in SKILL.md files"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply fixes (default is dry-run)",
    )
    parser.add_argument(
        "--skills-root", default=str(SKILLS_ROOT),
        help="Skills root directory",
    )
    args = parser.parse_args()
    root = Path(args.skills_root)

    if not root.exists():
        print(f"Error: {root} not found", file=sys.stderr)
        return 1

    report = apply_fixes(root, dry_run=not args.apply)
    mode = "APPLIED" if args.apply else "DRY RUN"

    print(f"[{mode}] category_fixed: {report['category_fixed']}")
    print(f"[{mode}] version_fixed: {report['version_fixed']}")

    if report["short_descriptions"]:
        print(f"\nShort descriptions ({len(report['short_descriptions'])}):")
        for s in report["short_descriptions"]:
            print(f"  {s['name']:40s} ({s['words']}w) {s['current']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
