#!/usr/bin/env python3
"""
audit-micro-skill-scripts.py — Classify stage micro-skill checklist items
as scriptable / judgment / already-scripted and identify candidates for
promotion to Level 2 (deterministic script) per .claude/rules/patterns.md.

Usage:
    uv run --no-project python scripts/work-queue/audit_micro_skill_scripts.py
    uv run --no-project python scripts/work-queue/audit_micro_skill_scripts.py --wrk WRK-1144
"""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Classification constants
# ---------------------------------------------------------------------------

BINARY_PATTERNS = [
    "exists", "matches", "passes", "generated", "present",
    "verify", "check", "count", "confirm", "run", "validate",
    "passed", "fail", "missing", "found", "absent",
]

JUDGMENT_PATTERNS = [
    "assess", "evaluate", "decide", "draft", "summarize",
    "investigate", "review", "explain", "document", "inspect",
    "consider", "think", "choose", "select", "determine",
]

HARD_GATE_STAGES = {1, 5, 7, 17}
MULTI_STAGE_THRESHOLD = 3
HIGH_PRIORITY_THRESHOLD = 3
MAX_PROPOSED_WRKS = 5


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_known_scripts(work_queue_dir: Path) -> set[str]:
    """Return stems of all .py and .sh files in scripts/work-queue/."""
    scripts = set()
    for ext in ("*.py", "*.sh"):
        for p in work_queue_dir.glob(ext):
            scripts.add(p.stem)
            scripts.add(p.name)
    return scripts


def classify(line: str, known_scripts: set[str]) -> str:
    """Classify a checklist line as already-scripted / judgment / scriptable.

    Priority order:
    1. already-scripted — if a known script name appears in the line
    2. judgment         — if a judgment-denylist keyword appears
    3. scriptable       — if a binary-check keyword appears
    4. judgment         — default-safe fallback
    """
    line_lower = line.lower()
    if any(s.lower() in line_lower for s in known_scripts):
        return "already-scripted"
    if any(j in line_lower for j in JUDGMENT_PATTERNS):
        return "judgment"
    if any(b in line_lower for b in BINARY_PATTERNS):
        return "scriptable"
    return "judgment"


def priority_score(item: dict) -> int:
    """Compute priority score for a classified item.

    Only scriptable items score > 0.  already-scripted and judgment items
    return 0 (no child WRK needed).
    """
    if item.get("cls") != "scriptable":
        return 0
    score = 0
    if item.get("stage") in HARD_GATE_STAGES:
        score += 3
    if item.get("n_stages", 1) >= MULTI_STAGE_THRESHOLD:
        score += 2
    return score


def extract_checklist_lines(content: str) -> list[str]:
    """Extract checklist lines from micro-skill markdown content.

    Recognises:
    - Numbered steps: lines starting with '<digit>. '
    - Checkbox style: lines starting with '- [ ] ' or '- [x] '
    """
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+\S", stripped):
            # numbered step — strip leading number
            lines.append(re.sub(r"^\d+\.\s+", "", stripped))
        elif re.match(r"^-\s+\[.?\]\s+\S", stripped):
            # checkbox style — strip checkbox prefix
            lines.append(re.sub(r"^-\s+\[.?\]\s+", "", stripped))
    return lines


def extract_stage_number(path: Path) -> int:
    """Extract numeric stage from filename like stage-05-user-review.md."""
    m = re.search(r"stage-(\d+)-", path.name)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Audit pipeline
# ---------------------------------------------------------------------------

def audit_stage_files(stages_dir: Path, known_scripts: set[str]) -> list[dict]:
    """Read all stage-NN-*.md files and classify each checklist item."""
    items = []
    for stage_file in sorted(stages_dir.glob("stage-*.md")):
        stage_num = extract_stage_number(stage_file)
        content = stage_file.read_text(encoding="utf-8")
        for line in extract_checklist_lines(content):
            cls = classify(line, known_scripts)
            items.append({
                "stage": stage_num,
                "stage_file": stage_file.name,
                "line": line,
                "cls": cls,
                "n_stages": 1,  # updated in dedup pass below
            })
    return _add_cross_stage_counts(items)


def _add_cross_stage_counts(items: list[dict]) -> list[dict]:
    """Count how many stages each normalised line text appears in."""
    from collections import Counter
    normalised = [re.sub(r"\s+", " ", i["line"].lower().strip()) for i in items]
    counts = Counter(normalised)
    for item, key in zip(items, normalised):
        item["n_stages"] = counts[key]
    return items


def build_report(items: list[dict], wrk_id: str = "WRK-1144") -> dict:
    """Build the YAML report structure from classified items."""
    scriptable = [i for i in items if i["cls"] == "scriptable"]
    judgment = [i for i in items if i["cls"] == "judgment"]
    already = [i for i in items if i["cls"] == "already-scripted"]

    # Score and rank scriptable items
    for item in scriptable:
        item["score"] = priority_score(item)
    ranked = sorted(scriptable, key=lambda x: x["score"], reverse=True)
    high_priority = [i for i in ranked if i["score"] >= HIGH_PRIORITY_THRESHOLD]

    # Proposed child WRKs (YAML only — human must approve before .md creation)
    proposed_wrks = []
    for i, candidate in enumerate(high_priority[:MAX_PROPOSED_WRKS], start=1):
        proposed_wrks.append({
            "proposed_title": f"chore(harness): script — {candidate['line'][:60].rstrip()}",
            "stage": candidate["stage"],
            "score": candidate["score"],
            "blocked_by": [wrk_id],
            "note": "PROPOSED ONLY — human must approve before creating .md file",
        })

    return {
        "wrk_id": wrk_id,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total": len(items),
            "scriptable": len(scriptable),
            "judgment": len(judgment),
            "already_scripted": len(already),
            "high_priority_count": len(high_priority),
        },
        "high_priority": [
            {"stage": i["stage"], "line": i["line"], "score": i["score"],
             "stage_file": i["stage_file"]}
            for i in high_priority
        ],
        "proposed_wrks": proposed_wrks,
        "all_items": [
            {"stage": i["stage"], "cls": i["cls"], "n_stages": i["n_stages"],
             "line": i["line"], "stage_file": i["stage_file"]}
            for i in items
        ],
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Audit micro-skill checklist items")
    parser.add_argument("--wrk", default="WRK-1144", help="WRK ID for output report")
    parser.add_argument("--stages-dir", help="Override path to stages/ directory")
    parser.add_argument("--output", help="Override output YAML path")
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parents[2]
    stages_dir = Path(args.stages_dir) if args.stages_dir else \
        workspace / ".claude/skills/workspace-hub/stages"
    work_queue_dir = workspace / "scripts/work-queue"
    output_path = Path(args.output) if args.output else \
        workspace / f".claude/work-queue/assets/{args.wrk}/micro-skill-script-candidates.yaml"

    if not stages_dir.is_dir():
        print(f"✖ stages dir not found: {stages_dir}", file=sys.stderr)
        return 1

    known_scripts = load_known_scripts(work_queue_dir)
    items = audit_stage_files(stages_dir, known_scripts)
    report = build_report(items, wrk_id=args.wrk)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(report, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    s = report["summary"]
    print(f"✔ {output_path}")
    print(f"  total={s['total']}  scriptable={s['scriptable']}  "
          f"judgment={s['judgment']}  already-scripted={s['already_scripted']}")
    print(f"  high-priority candidates: {s['high_priority_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
