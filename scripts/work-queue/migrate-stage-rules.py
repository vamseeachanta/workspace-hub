#!/usr/bin/env python3
"""
migrate-stage-rules.py — Extract stage-specific sections from work-queue-workflow/SKILL.md.

Uses an explicit SECTION_MAP to route named sections to target stage numbers.
Cross-cutting rules (terminology, gate policy table, orchestrator pattern) are NOT extracted
and must stay in SKILL.md.

Usage:
    uv run --no-project python scripts/work-queue/migrate-stage-rules.py [--apply]

Without --apply: prints the migration plan to stdout (dry-run).
With --apply:    appends extracted content to the target stage micro-skill files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = REPO_ROOT / ".claude" / "skills" / "workspace-hub" / "work-queue-workflow" / "SKILL.md"
STAGES_DIR = REPO_ROOT / ".claude" / "skills" / "workspace-hub" / "stages"

# Explicit mapping: section heading pattern → target stage numbers
# Only stage-specific sections are listed here.
# Cross-cutting content (terminology, gate policy, orchestrator pattern) stays in SKILL.md.
SECTION_MAP: dict[str, list[int]] = {
    "Stage 4 — Plan Draft Creation": [4],
    "Stage 5 — Plan Draft (Human-in-Loop Interactive)": [5],
    "Stage 6 — Cross-Review": [6],
    "Stage 8 — Claim/Activation": [8],
    "Stage 10 — Work Execution": [10],
    "Lifecycle HTML — Deliverables Section": [17, 18],
    "Stage-Evidence Path After Close": [19],
}


def extract_section(content: str, heading: str) -> str | None:
    """Extract a markdown section by its heading. Returns None if not found."""
    # Match '### <heading>' at any level (##, ###, ####)
    pattern = rf"^(#{1,4})\s+{re.escape(heading)}\s*$"
    lines = content.splitlines(keepends=True)
    start_idx = None
    level = None
    for i, line in enumerate(lines):
        m = re.match(pattern, line, re.MULTILINE)
        if m:
            start_idx = i
            level = len(m.group(1))
            break
    if start_idx is None:
        return None
    # Collect until next heading of same or higher level
    section_lines = [lines[start_idx]]
    for line in lines[start_idx + 1:]:
        m = re.match(r"^(#{1,6})\s", line)
        if m and len(m.group(1)) <= level:
            break
        section_lines.append(line)
    return "".join(section_lines).rstrip()


def find_stage_file(stage: int) -> Path | None:
    """Find the micro-skill file for a given stage number."""
    import glob
    matches = sorted(glob.glob(str(STAGES_DIR / f"stage-{stage:02d}-*.md")))
    return Path(matches[0]) if matches else None


def run(apply: bool = False) -> int:
    if not SKILL_MD.exists():
        print(f"ERROR: SKILL.md not found: {SKILL_MD}", file=sys.stderr)
        return 1

    content = SKILL_MD.read_text(encoding="utf-8")
    errors = 0

    for heading, stages in SECTION_MAP.items():
        extracted = extract_section(content, heading)
        if extracted is None:
            print(f"WARN: Section not found in SKILL.md: '{heading}'")
            continue

        for stage in stages:
            target = find_stage_file(stage)
            if target is None:
                print(f"WARN: No micro-skill file found for stage {stage}")
                errors += 1
                continue

            print(f"\n{'='*60}")
            print(f"Section: '{heading}' → stage-{stage:02d} ({target.name})")
            print(f"{'='*60}")
            print(extracted[:400] + ("..." if len(extracted) > 400 else ""))

            if apply:
                existing = target.read_text(encoding="utf-8")
                marker = f"## Migrated from SKILL.md: {heading}"
                if marker in existing:
                    print(f"  → Already present in {target.name}, skipping.")
                else:
                    target.write_text(
                        existing.rstrip() + f"\n\n## Migrated from SKILL.md: {heading}\n\n"
                        + extracted + "\n",
                        encoding="utf-8",
                    )
                    print(f"  → Appended to {target.name}")

    if not apply:
        print(f"\n{'='*60}")
        print("Dry-run complete. Re-run with --apply to write changes.")
        print(f"Sections mapped: {len(SECTION_MAP)}")
    return errors


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    sys.exit(run(apply=apply))
