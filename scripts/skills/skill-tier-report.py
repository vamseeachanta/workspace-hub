#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Skill Quality Tier Report — ranked tier list with Tier D flagging.

Usage:
    uv run --no-project python scripts/skills/skill-tier-report.py
    uv run --no-project python scripts/skills/skill-tier-report.py --format yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Ensure scripts/skills is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_skill_lib import parse_frontmatter
from skill_tier_lib import classify_tier, tier_distribution


SKILLS_ROOT = Path(".claude/skills")


def discover_and_classify(skills_root: Path) -> list[dict]:
    """Discover all SKILL.md files and classify each."""
    results: list[dict] = []
    for skill_file in sorted(skills_root.rglob("SKILL.md")):
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(content)
        name = (meta.get("name") if meta else None) or skill_file.parent.name
        tier = classify_tier(meta, body)
        word_count = len(body.split())
        results.append({
            "path": str(skill_file),
            "name": name,
            "tier": tier,
            "word_count": word_count,
        })
    return results


def format_human(results: list[dict], dist: dict[str, int]) -> str:
    """Format as human-readable text."""
    lines: list[str] = []
    total = len(results)
    lines.append("=" * 60)
    lines.append("  SKILL QUALITY TIER REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append("DISTRIBUTION")
    lines.append("-" * 40)
    for tier in ("A", "B", "C", "D"):
        count = dist[tier]
        pct = (count / total * 100) if total else 0
        lines.append(f"  Tier {tier}: {count:3d}  ({pct:5.1f}%)")
    lines.append(f"  Total:  {total:3d}")
    lines.append("")

    # Tier D flagged items
    tier_d = [r for r in results if r["tier"] == "D"]
    if tier_d:
        lines.append(f"TIER D — DECOMPOSITION CANDIDATES ({len(tier_d)})")
        lines.append("-" * 40)
        for r in sorted(tier_d, key=lambda x: -x["word_count"]):
            lines.append(f"  {r['name']:40s} {r['word_count']:5d} words")
        lines.append("")

    # Full ranked list
    tier_order = {"A": 0, "B": 1, "C": 2, "D": 3}
    ranked = sorted(results, key=lambda x: (tier_order.get(x["tier"], 9), x["name"]))
    lines.append("FULL TIER LIST")
    lines.append("-" * 40)
    for r in ranked:
        lines.append(f"  [{r['tier']}] {r['name']:40s} {r['word_count']:5d}w")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_yaml(results: list[dict], dist: dict[str, int]) -> str:
    """Format as YAML output."""
    tier_d = [r for r in results if r["tier"] == "D"]
    data = {
        "tier_distribution": dist,
        "total_skills": len(results),
        "tier_d_flagged": [
            {"name": r["name"], "path": r["path"], "word_count": r["word_count"]}
            for r in sorted(tier_d, key=lambda x: -x["word_count"])
        ],
        "skills": [
            {"name": r["name"], "tier": r["tier"], "word_count": r["word_count"]}
            for r in sorted(results, key=lambda x: x["name"])
        ],
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False, width=120)


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill Quality Tier Report")
    parser.add_argument(
        "--format", choices=["human", "yaml"], default="human",
        help="Output format",
    )
    parser.add_argument("--output", help="Write report to file")
    parser.add_argument("--root", default=".", help="Workspace root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skills_dir = root / SKILLS_ROOT
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}", file=sys.stderr)
        return 2

    results = discover_and_classify(skills_dir)
    print(f"Classified {len(results)} skills", file=sys.stderr)

    tiers = [r["tier"] for r in results]
    dist = tier_distribution(tiers)

    if args.format == "yaml":
        output = format_yaml(results, dist)
    else:
        output = format_human(results, dist)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
