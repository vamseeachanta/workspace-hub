#!/usr/bin/env python3
"""weekly-trends.py — Compute weekly trend metrics for learning feedback loop.

Metrics:
  1. Hook violation rate (drift counts per day)
  2. One-shot success rate (sessions without corrections)
  3. Stage velocity (median seconds per WRK stage)

Writes JSONL to .claude/state/trends/weekly-trends.jsonl and a markdown
summary to .claude/state/trends/weekly-summary.md.

Called by comprehensive-learning.sh as part of the nightly pipeline.
"""

import json
import os
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path

WS_HUB = Path(__file__).resolve().parent.parent.parent
STATE_DIR = WS_HUB / ".claude" / "state"
TRENDS_DIR = STATE_DIR / "trends"
TRENDS_JSONL = TRENDS_DIR / "weekly-trends.jsonl"
SUMMARY_MD = TRENDS_DIR / "weekly-summary.md"
CORRECTIONS_DIR = STATE_DIR / "corrections"
SIGNALS_DIR = STATE_DIR / "session-signals"
WQ_ASSETS = WS_HUB / ".claude" / "work-queue" / "assets"


def get_week_key(dt):
    """ISO week key like '2026-W12'."""
    return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"


def compute_drift_metrics():
    """Parse drift-counts.jsonl for violation rates."""
    drift_file = SIGNALS_DIR / "drift-counts.jsonl"
    if not drift_file.exists():
        return {}
    weekly = {}
    with open(drift_file) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = rec.get("ts", "")
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue
            wk = get_week_key(dt)
            if wk not in weekly:
                weekly[wk] = {"python_runtime": 0, "file_placement": 0, "git_workflow": 0, "days": set()}
            weekly[wk]["python_runtime"] += rec.get("python_runtime_violations", 0)
            weekly[wk]["file_placement"] += rec.get("file_placement_violations", 0)
            weekly[wk]["git_workflow"] += rec.get("git_workflow_violations", 0)
            weekly[wk]["days"].add(dt.strftime("%Y-%m-%d"))
    # Convert sets to counts
    for wk in weekly:
        n = len(weekly[wk].pop("days")) or 1
        weekly[wk]["violations_per_day"] = round(
            (weekly[wk]["python_runtime"] + weekly[wk]["file_placement"] + weekly[wk]["git_workflow"]) / n, 1
        )
    return weekly


def compute_correction_metrics():
    """Count corrections per week based on file timestamps."""
    if not CORRECTIONS_DIR.exists():
        return {}
    weekly = {}
    for f in CORRECTIONS_DIR.glob("*.yaml"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        wk = get_week_key(mtime)
        weekly[wk] = weekly.get(wk, 0) + 1
    return weekly


def compute_session_metrics():
    """Count sessions per week and compute one-shot rate."""
    weekly = {}
    for sig_file in sorted(SIGNALS_DIR.glob("2026-*.jsonl")):
        # Extract date from filename
        match = re.search(r"(\d{4}-\d{2}-\d{2})", sig_file.name)
        if not match:
            continue
        try:
            dt = datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            continue
        wk = get_week_key(dt)
        if wk not in weekly:
            weekly[wk] = {"sessions": 0}
        # Count sessions in file
        with open(sig_file) as f:
            for line in f:
                try:
                    json.loads(line)
                    weekly[wk]["sessions"] += 1
                except json.JSONDecodeError:
                    continue
    return weekly


def compute_stage_velocity():
    """Compute median stage duration from stage-timing evidence files."""
    durations = {}  # week -> list of durations
    for asset_dir in WQ_ASSETS.iterdir():
        if not asset_dir.is_dir():
            continue
        evidence = asset_dir / "evidence"
        if not evidence.exists():
            continue
        for timing_file in evidence.glob("stage-timing-*.yaml"):
            try:
                content = timing_file.read_text()
            except OSError:
                continue
            # Extract duration_s and started_at
            dur_match = re.findall(r"duration_s:\s*([\d.]+)", content)
            start_match = re.search(r"started_at:\s*[\"']?([^\"'\n]+)", content)
            if not dur_match or not start_match:
                continue
            try:
                dt = datetime.fromisoformat(start_match.group(1).replace("Z", "+00:00").strip("\"'"))
                duration = float(dur_match[-1])  # Take last duration (may have updates)
            except (ValueError, TypeError):
                continue
            wk = get_week_key(dt)
            if wk not in durations:
                durations[wk] = []
            durations[wk].append(duration)

    # Compute medians
    result = {}
    for wk, durs in durations.items():
        durs.sort()
        n = len(durs)
        median = durs[n // 2] if n % 2 else (durs[n // 2 - 1] + durs[n // 2]) / 2
        result[wk] = {"median_stage_s": round(median, 1), "stages_completed": n}
    return result


def main():
    TRENDS_DIR.mkdir(parents=True, exist_ok=True)

    drift = compute_drift_metrics()
    corrections = compute_correction_metrics()
    sessions = compute_session_metrics()
    velocity = compute_stage_velocity()

    # Collect all weeks
    all_weeks = sorted(set(list(drift.keys()) + list(corrections.keys()) +
                           list(sessions.keys()) + list(velocity.keys())))

    # Build weekly records
    records = []
    for wk in all_weeks:
        rec = {
            "week": wk,
            "violations_per_day": drift.get(wk, {}).get("violations_per_day", 0),
            "corrections": corrections.get(wk, 0),
            "sessions": sessions.get(wk, {}).get("sessions", 0),
            "median_stage_s": velocity.get(wk, {}).get("median_stage_s", 0),
            "stages_completed": velocity.get(wk, {}).get("stages_completed", 0),
        }
        # One-shot rate: sessions without corrections / total sessions
        if rec["sessions"] > 0:
            rec["one_shot_rate"] = round(max(0, rec["sessions"] - rec["corrections"]) / rec["sessions"] * 100, 1)
        else:
            rec["one_shot_rate"] = None
        records.append(rec)

    # Write JSONL
    with open(TRENDS_JSONL, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    # Write markdown summary (last 4 weeks)
    recent = records[-4:] if len(records) >= 4 else records
    lines = ["# Weekly Trend Summary", "",
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "| Week | Violations/day | Corrections | Sessions | One-shot % | Median stage (s) | Stages |",
             "|------|---------------|-------------|----------|-----------|-----------------|--------|"]
    for r in recent:
        os_rate = f"{r['one_shot_rate']}%" if r["one_shot_rate"] is not None else "n/a"
        lines.append(f"| {r['week']} | {r['violations_per_day']} | {r['corrections']} | "
                     f"{r['sessions']} | {os_rate} | {r['median_stage_s']} | {r['stages_completed']} |")

    # Week-over-week delta
    if len(recent) >= 2:
        prev, curr = recent[-2], recent[-1]
        lines.extend(["", "## Week-over-Week Delta", ""])
        for metric in ["violations_per_day", "corrections", "sessions", "median_stage_s", "stages_completed"]:
            p, c = prev[metric] or 0, curr[metric] or 0
            delta = c - p
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            lines.append(f"- **{metric}**: {p} → {c} ({arrow} {abs(delta):.1f})")

    lines.append("")
    SUMMARY_MD.write_text("\n".join(lines))

    print(f"PHASE_RESULT|trends|DONE|{len(records)} weeks tracked, summary at {SUMMARY_MD.relative_to(WS_HUB)}")


if __name__ == "__main__":
    main()
