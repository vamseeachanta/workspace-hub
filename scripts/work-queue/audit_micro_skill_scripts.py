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
import textwrap
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Classification constants
# ---------------------------------------------------------------------------

# Single-word patterns use word boundaries; multi-word stay as phrases.
_BINARY_WORDS = [
    "exists", "matches", "passes", "generated", "present", "verify",
    "check", "count", "confirm", "validate", "passed", "fail",
    "missing", "found", "absent",
]
# Compile as word-boundary patterns to avoid substring false positives.
BINARY_PATTERNS = [re.compile(r"\b" + re.escape(w) + r"\b") for w in _BINARY_WORDS]

_JUDGMENT_WORDS = [
    "assess", "evaluate", "decide", "draft", "summarize", "investigate",
    "review", "explain", "document", "inspect", "consider", "think",
    "choose", "select", "determine",
]
JUDGMENT_PATTERNS = [re.compile(r"\b" + re.escape(w) + r"\b") for w in _JUDGMENT_WORDS]

# Write-action prefixes that should never be classified scriptable regardless of keywords.
WRITE_PREFIXES = re.compile(r"^\s*(write|create|generate|produce|output|emit)\b", re.IGNORECASE)

HARD_GATE_STAGES = {1, 5, 7, 17}
MULTI_STAGE_THRESHOLD = 3
HIGH_PRIORITY_THRESHOLD = 3
MAX_PROPOSED_WRKS = 5


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_known_scripts(work_queue_dir: Path) -> set[str]:
    """Return full filenames of all .py and .sh files in scripts/work-queue/."""
    scripts = set()
    for ext in ("*.py", "*.sh"):
        for p in work_queue_dir.glob(ext):
            scripts.add(p.name)  # full name only — stems skipped to avoid substring collisions
    return scripts


def classify(line: str, known_scripts: set[str]) -> str:
    """Classify a checklist line as already-scripted / judgment / scriptable.

    Priority order:
    1. already-scripted — a known script *filename* appears as a word token
    2. judgment         — write-action prefix OR judgment-denylist keyword matches
    3. scriptable       — binary-check keyword matches (word boundary)
    4. judgment         — default-safe fallback
    """
    line_lower = line.lower()
    # 1. already-scripted: full filename must appear as a token (not substring of a word)
    for script in known_scripts:
        if re.search(r"\b" + re.escape(script.lower()) + r"\b", line_lower):
            return "already-scripted"
    # 2. judgment: write-action prefix or denylist keyword
    if WRITE_PREFIXES.match(line):
        return "judgment"
    if any(p.search(line_lower) for p in JUDGMENT_PATTERNS):
        return "judgment"
    # 3. scriptable: binary-check keyword with word boundary
    if any(p.search(line_lower) for p in BINARY_PATTERNS):
        return "scriptable"
    return "judgment"


def priority_score(item: dict) -> int:
    """Compute priority score for a classified item.

    Only scriptable items score > 0.  already-scripted and judgment return 0.
    """
    if item.get("cls") != "scriptable":
        return 0
    score = 0
    if item.get("stage") in HARD_GATE_STAGES:
        score += 3
    if item.get("n_distinct_stages", 1) >= MULTI_STAGE_THRESHOLD:
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
            lines.append(re.sub(r"^\d+\.\s+", "", stripped))
        elif re.match(r"^[-*+]\s+\[.?\]\s+\S", stripped):
            lines.append(re.sub(r"^[-*+]\s+\[.?\]\s+", "", stripped))
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
            })
    return _add_cross_stage_counts(items)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _add_cross_stage_counts(items: list[dict]) -> list[dict]:
    """Count how many *distinct stage numbers* each normalised line appears in."""
    # Map normalised text → set of stage numbers
    stage_sets: dict[str, set[int]] = defaultdict(set)
    for item in items:
        stage_sets[_normalise(item["line"])].add(item["stage"])
    for item in items:
        item["n_distinct_stages"] = len(stage_sets[_normalise(item["line"])])
    return items


def _make_wrk_title(line: str, stage: int) -> str:
    """Generate an actionable child WRK title with stage context."""
    short = textwrap.shorten(line, width=55, placeholder="...")
    return f"chore(harness): stage-{stage:02d} script — {short}"


def build_report(items: list[dict], wrk_id: str = "WRK-1144") -> dict:
    """Build the YAML report structure from classified items."""
    scriptable = [i for i in items if i["cls"] == "scriptable"]
    judgment = [i for i in items if i["cls"] == "judgment"]
    already = [i for i in items if i["cls"] == "already-scripted"]

    for item in scriptable:
        item["score"] = priority_score(item)
    ranked = sorted(scriptable, key=lambda x: x["score"], reverse=True)
    high_priority = [i for i in ranked if i["score"] >= HIGH_PRIORITY_THRESHOLD]

    # Deduplicate proposed WRKs by (normalised_line, stage)
    seen: set[tuple[str, int]] = set()
    proposed_wrks = []
    for candidate in high_priority:
        key = (_normalise(candidate["line"]), candidate["stage"])
        if key in seen:
            continue
        seen.add(key)
        if len(proposed_wrks) >= MAX_PROPOSED_WRKS:
            break
        proposed_wrks.append({
            "proposed_title": _make_wrk_title(candidate["line"], candidate["stage"]),
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
            "proposed_wrk_count": len(proposed_wrks),
        },
        "high_priority": [
            {"stage": i["stage"], "line": i["line"], "score": i["score"],
             "stage_file": i["stage_file"], "n_distinct_stages": i["n_distinct_stages"]}
            for i in high_priority
        ],
        "proposed_wrks": proposed_wrks,
        "all_items": [
            {"stage": i["stage"], "cls": i["cls"],
             "n_distinct_stages": i["n_distinct_stages"],
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
    print(f"  high-priority: {s['high_priority_count']}  proposed WRKs: {s['proposed_wrk_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
