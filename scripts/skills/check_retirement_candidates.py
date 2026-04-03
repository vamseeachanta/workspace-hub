#!/usr/bin/env python3
"""check_retirement_candidates.py — Flag skills below retirement threshold.

Threshold: baseline_usage_rate < 0.05 AND calls_in_period < 10.
SKIP if either field is absent/null.

Always exits 0 (non-blocking).
"""
import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check skill retirement candidates")
    parser.add_argument(
        "--scores-file",
        default=".claude/state/skill-scores.yaml",
        help="Path to skill-scores.yaml (default: .claude/state/skill-scores.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        default=".claude/state/skill-retirement-candidates",
        help="Directory to write retirement candidate JSON (default: .claude/state/skill-retirement-candidates)",
    )
    return parser.parse_args()


def load_scores(scores_file: Path) -> dict:
    """Load skill-scores.yaml — try PyYAML first, fallback to simple parser."""
    if not scores_file.exists():
        return {}
    try:
        import yaml  # type: ignore[import]
        with scores_file.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data.get("skills", {})
    except ImportError:
        pass
    return _parse_scores_simple(scores_file.read_text(encoding="utf-8"))


def _parse_scores_simple(text: str) -> dict:
    """Simple line parser for skill-scores.yaml."""
    skills: dict = {}
    current: str | None = None
    in_skills = False

    for line in text.splitlines():
        stripped = line.rstrip()
        if stripped.strip() == "skills:":
            in_skills = True
            continue
        if not in_skills:
            continue
        # Top-level skill name (2-space indent, ends with :)
        if stripped.startswith("  ") and not stripped.startswith("    ") and stripped.strip().endswith(":"):
            current = stripped.strip()[:-1]
            skills[current] = {}
        elif current and stripped.startswith("    ") and ":" in stripped:
            key, _, val = stripped.strip().partition(":")
            val = val.strip().strip("'\"#").split()[0] if val.strip() else ""
            if val and val not in ("null", "~", ""):
                try:
                    skills[current][key.strip()] = float(val)
                except ValueError:
                    skills[current][key.strip()] = val
    return skills


def check_threshold(skill_name: str, entry: dict) -> str:
    """Return 'candidate', 'skip', or 'ok'."""
    if entry.get("tier") and str(entry.get("tier")).lower() != "dead":
        return "ok"

    rate = entry.get("baseline_usage_rate")
    calls = entry.get("calls_in_period")

    if rate is None or calls is None:
        return "skip"

    try:
        rate_f = float(rate)
        calls_i = int(float(calls))
    except (TypeError, ValueError):
        return "skip"

    if rate_f < 0.05 and calls_i < 10:
        return "candidate"
    return "ok"


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    scores_file = repo_root / args.scores_file
    output_dir = repo_root / args.output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    skills = load_scores(scores_file)
    if not skills:
        print(f"INFO: No skill data found in {scores_file} (file may not exist yet)")
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = timestamp[:10]

    candidates = []
    for skill_name, entry in skills.items():
        status = check_threshold(skill_name, entry)
        rate = entry.get("baseline_usage_rate", "n/a")
        calls = entry.get("calls_in_period", "n/a")

        if status == "candidate":
            print(
                f"RETIREMENT CANDIDATE: {skill_name} (rate={rate}, calls={calls})"
            )
            candidates.append({
                "skill_name": skill_name,
                "baseline_usage_rate": rate,
                "calls_in_period": calls,
            })
        elif status == "skip":
            print(f"SKIP: {skill_name} — missing usage data")

    output_path = output_dir / f"{date_str}.json"
    payload = {
        "generated_at": timestamp,
        "candidates": candidates,
        "total_skills_checked": len(skills),
    }
    tmp = output_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.rename(output_path)

    print(
        f"\n{len(candidates)} flagged skill(s) from {len(skills)} checked. "
        f"See {output_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
