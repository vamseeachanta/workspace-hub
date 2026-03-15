"""Compute skill preference weights from execution history (WRK-5088).

Reads skill-executions.jsonl (from skill-execution-tracker) and produces
skill-preferences.yaml with frequency-based weights for routing decisions.

Usage:
    uv run --no-project python scripts/skills/skill_preference_weights.py [--input PATH] [--output PATH] [--min-samples N]
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml


# Generic tool names to exclude (not real skills)
EXCLUDE_NAMES = {"Skill", "Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"}


def load_executions(path: Path) -> list[dict]:
    """Load skill execution records from JSONL."""
    if not path.exists():
        return []
    entries: list[dict] = []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return entries
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def compute_preferences(executions: list[dict], min_samples: int = 5) -> list[dict]:
    """Compute frequency-based preference weights per skill."""
    if not executions:
        return []

    # Aggregate by skill name
    stats: dict[str, dict] = defaultdict(lambda: {
        "count": 0,
        "sessions": set(),
        "total_duration": 0.0,
    })

    for ex in executions:
        name = ex.get("skill_name", "")
        if not name or name in EXCLUDE_NAMES:
            continue
        s = stats[name]
        s["count"] += 1
        s["sessions"].add(ex.get("session_id", ""))
        s["total_duration"] += ex.get("duration_s", 0)

    # Filter by minimum samples and build results
    results = []
    for name, s in stats.items():
        if s["count"] < min_samples:
            continue
        results.append({
            "skill": name,
            "invocation_count": s["count"],
            "unique_sessions": len(s["sessions"]),
            "avg_duration_s": round(s["total_duration"] / s["count"], 2),
            "weight": 0.0,  # normalized below
        })

    # Sort by frequency descending
    results.sort(key=lambda x: x["invocation_count"], reverse=True)

    # Normalize weights: top skill = 1.0, others proportional
    if results:
        max_count = results[0]["invocation_count"]
        for r in results:
            r["weight"] = round(r["invocation_count"] / max_count, 3)

    return results


def write_preferences_yaml(preferences: list[dict], output_path: Path) -> None:
    """Write preferences to YAML file."""
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "min_samples": 5,
        "total_skills": len(preferences),
        "preferences": preferences,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute skill preference weights")
    parser.add_argument("--input", default=".claude/state/skill-executions.jsonl")
    parser.add_argument("--output", default=".claude/state/skill-preferences.yaml")
    parser.add_argument("--min-samples", type=int, default=5)
    args = parser.parse_args()

    executions = load_executions(Path(args.input))
    preferences = compute_preferences(executions, min_samples=args.min_samples)
    write_preferences_yaml(preferences, Path(args.output))

    print(f"Computed preferences for {len(preferences)} skills (min {args.min_samples} samples) -> {args.output}")
    for p in preferences[:10]:
        print(f"  {p['skill']}: weight={p['weight']} ({p['invocation_count']} invocations, {p['unique_sessions']} sessions)")


if __name__ == "__main__":
    main()
