#!/usr/bin/env python3
"""skill-invocation-scanner.py — #2320

Mine hermes session JSONL logs for skill-activity events, emit per-skill
invocation + distinct-session counts, and write a PII-safe JSON report.

Event schema (flat envelope, verified empirically):
  { ts, hook, tool, hermes_tool, project, repo, model, session_id,
    file, skill_name }

A "skill invocation signal" is any event where `skill_name` is set. Events
without `skill_name` are ignored (they fired outside any skill context).

Scope is explicitly the available retention window (~17 days today, not a
hardcoded 90d — see plan's "Execution-time revisions"). The output surfaces
`coverage_days` so downstream consumers (e.g., scripts/skills/skill-usage-report.py)
can gate their demotion logic with MIN_COVERAGE_DAYS.

Usage:
  uv run --no-project python scripts/skills/skill-invocation-scanner.py \\
      --sessions-dir logs/orchestrator/hermes \\
      --skills-root .claude/skills \\
      [--output .claude/state/skill-invocations/YYYY-MM-DD.json]

PII note: only `skill_name`, `session_id`, `ts`, and counts are propagated.
File paths, prompts, tool args, and stdouts/stderrs never leave the scanner.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MIN_COVERAGE = 14  # days — shared with skill-usage-report.py demotion rule


def _parse_ts(ts: str):
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None
    # Normalize to tz-aware UTC — real hermes logs omit the tz suffix.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def scan_sessions(sessions_dir: Path):
    """Walk session_YYYYMMDD.jsonl files, collect per-skill timestamps + session IDs.

    Returns (event_ts, session_ts, coverage_days) where:
      event_ts   : dict[str, list[str]]  — skill_name -> raw ts strings.
      session_ts : dict[str, set[str]]   — skill_name -> set of session_id values.
      coverage_days : int — days between oldest and newest event seen.
    """
    event_ts: dict[str, list[str]] = defaultdict(list)
    session_ts: dict[str, set[str]] = defaultdict(set)
    oldest = None
    newest = None

    for path in sorted(Path(sessions_dir).glob("session_*.jsonl")):
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue  # silently skip malformed lines
                sn = event.get("skill_name")
                if not sn:
                    continue
                ts_str = event.get("ts")
                dt = _parse_ts(ts_str) if ts_str else None
                if dt is None:
                    continue
                sid = event.get("session_id")
                event_ts[sn].append(ts_str)
                if sid:
                    session_ts[sn].add(sid)
                oldest = dt if oldest is None or dt < oldest else oldest
                newest = dt if newest is None or dt > newest else newest

    coverage_days = (newest - oldest).days if oldest and newest else 0
    return event_ts, session_ts, coverage_days


def discover_skills(skills_root: Path):
    """Walk .claude/skills for SKILL.md, yield the relative skill name."""
    skills = []
    root = Path(skills_root)
    for skill_md in root.rglob("SKILL.md"):
        rel = skill_md.parent.relative_to(root).as_posix()
        skills.append(rel)
    return sorted(skills)


def classify(event_ts, session_ts, coverage_days: int, skills_root: Path):
    """Produce one row per discovered skill. Zero-invocation rows included."""
    now = datetime.now(timezone.utc)
    rows = []
    for skill in discover_skills(skills_root):
        ts_list = event_ts.get(skill, [])
        sessions = session_ts.get(skill, set())
        last_used = max(ts_list) if ts_list else None
        days_since = None
        if last_used:
            dt = _parse_ts(last_used)
            if dt is not None:
                days_since = (now - dt).days
        rows.append(
            {
                "skill": skill,
                "invocations_available_days": len(ts_list),
                "session_count_available_days": len(sessions),
                "coverage_days": coverage_days,
                "last_used": last_used,
                "days_since_last_use": days_since,
            }
        )
    return rows


def should_demote(session_count: int, coverage_days: int, min_coverage: int = DEFAULT_MIN_COVERAGE) -> bool:
    """Shared demotion rule used by skill-usage-report.py.

    Demote only when (a) there is enough data to be confident AND (b) the skill
    saw zero distinct sessions in the observed window.
    """
    return coverage_days >= min_coverage and session_count == 0


def write_output(payload: dict, out_file: Path) -> None:
    """Persist the report. Explicit whitelist — no extra fields slip through."""
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    allowed_row_keys = {
        "skill",
        "invocations_available_days",
        "session_count_available_days",
        "coverage_days",
        "last_used",
        "days_since_last_use",
    }
    allowed_top = {"coverage_days", "generated_at", "rows"}
    filtered_rows = []
    for row in payload.get("rows", []):
        filtered_rows.append({k: v for k, v in row.items() if k in allowed_row_keys})
    safe_payload = {k: v for k, v in payload.items() if k in allowed_top}
    safe_payload["rows"] = filtered_rows
    with open(out_file, "w") as f:
        json.dump(safe_payload, f, indent=2, default=str)


def _main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan hermes session logs for skill invocations")
    p.add_argument("--sessions-dir", type=Path, required=True,
                   help="Directory containing session_YYYYMMDD.jsonl files")
    p.add_argument("--skills-root", type=Path, required=True,
                   help="Root of .claude/skills/ — walked for SKILL.md files")
    p.add_argument("--output", type=Path, default=None,
                   help="Output JSON path (default: .claude/state/skill-invocations/YYYY-MM-DD.json)")
    args = p.parse_args(argv)

    event_ts, session_ts, coverage = scan_sessions(args.sessions_dir)
    rows = classify(event_ts, session_ts, coverage, args.skills_root)
    out = args.output or Path(".claude/state/skill-invocations") / f"{datetime.now().date().isoformat()}.json"
    payload = {
        "coverage_days": coverage,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    write_output(payload, out)
    print(f"wrote {len(rows)} skill rows ({coverage}d coverage) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
