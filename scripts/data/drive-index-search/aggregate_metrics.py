#!/usr/bin/env python3
"""Weekly counts-only aggregate of drive-index-search metrics (#3340, epic #3333).

Reads the local gitignored JSONL logs (invocations.jsonl + nudges.jsonl) and
writes a committed, privacy-safe per-host weekly aggregate:

    data/drive-index-search/metrics/weekly/<ISO-week>-<hostname>.json

Per-host filenames (plan review r1 F3) avoid cross-machine clobber; the 30-day
review merges per-host files (aggregate-of-aggregates).

Privacy by construction (plan D5): the aggregate carries ONLY counts, rates,
and medians — never query hashes, session-id values, paths, or raw queries.

`nudges_log_absent` reports "nudges.jsonl does not exist" DISTINCTLY from
"0 nudges this week" (plan review r1 F5) so a silently-lost denominator is
visible at review time.

Usage:
    python3 scripts/data/drive-index-search/aggregate_metrics.py [--week 2026-W27]
        [--metrics-dir <dir>] [--repo-root <dir>]
"""
from __future__ import annotations

import argparse
import json
import socket
import statistics
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# The hit-score threshold lives ONLY here as a named constant (plan review r1
# F7). D7 and the playbook cite HIT_SCORE_MIN, never the literal. The #3335
# merge score is normalized to [0, 1].
HIT_SCORE_MIN = 0.3

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_METRICS_DIR = REPO_ROOT / "data" / "drive-index-search" / "metrics"


def _iso_week(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _week_bounds(week: str) -> tuple[date, date]:
    year_s, week_s = week.split("-W")
    start = date.fromisocalendar(int(year_s), int(week_s), 1)
    return start, start + timedelta(days=7)


def _parse_jsonl(path: Path, week: str) -> tuple[list[dict], int]:
    """Return (lines whose ts falls in week, malformed count). Missing file -> ([], 0)."""
    rows: list[dict] = []
    malformed = 0
    if not path.exists():
        return rows, malformed
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
            ts = datetime.fromisoformat(str(row["ts"]).replace("Z", "+00:00"))
        except Exception:
            malformed += 1
            continue
        if _iso_week(ts) == week:
            rows.append(row)
    return rows, malformed


def _frac(rows: list[dict], predicate) -> float | None:
    if not rows:
        return None
    return round(sum(1 for row in rows if predicate(row)) / len(rows), 4)


def _sessions(rows: list[dict]) -> set[str]:
    return {
        str(row.get("session"))
        for row in rows
        if row.get("session") and row.get("session") != "unknown"
    }


def _plans_citing_drive_paths(repo_root: Path, week: str) -> int:
    """Used-in-plan proxy (plan D4): plans touched this week citing drive paths.

    Known caveats (plan r1 F6): counts citations not usefulness, and UNDERCOUNTS
    when de-id redaction removes the path string entirely. Fail-open to 0.
    """
    try:
        start, end = _week_bounds(week)
        out = subprocess.run(
            [
                "git", "log", "--name-only", "--pretty=format:",
                f"--since={start.isoformat()}", f"--until={end.isoformat()}",
                "--", "docs/plans",
            ],
            cwd=repo_root, capture_output=True, text=True, timeout=60, check=False,
        )
        count = 0
        for name in sorted({line.strip() for line in out.stdout.splitlines() if line.strip()}):
            plan_path = repo_root / name
            if not plan_path.is_file():
                continue
            text = plan_path.read_text(encoding="utf-8", errors="replace")
            if "/mnt/ace" in text or "/mnt/dde" in text:  # abs-path-allowed
                count += 1
        return count
    except Exception:
        return 0


def build_aggregate(metrics_dir: Path, week: str, repo_root: Path) -> dict:
    inv, inv_malformed = _parse_jsonl(metrics_dir / "invocations.jsonl", week)
    nudges_path = metrics_dir / "nudges.jsonl"
    nudges_log_absent = not nudges_path.exists()
    nudges, nudge_malformed = _parse_jsonl(nudges_path, week)

    by_caller: dict[str, int] = {}
    for row in inv:
        caller = str(row.get("caller") or "manual")
        by_caller[caller] = by_caller.get(caller, 0) + 1

    durations = [row["duration_ms"] for row in inv if isinstance(row.get("duration_ms"), (int, float))]
    nudge_sessions = _sessions(nudges)
    conversion = None
    if nudge_sessions and not nudges_log_absent:
        conversion = round(len(nudge_sessions & _sessions(inv)) / len(nudge_sessions), 4)

    return {
        "week": week,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "invocations": len(inv),
        "by_caller": by_caller,
        "hit_rate": _frac(
            inv,
            lambda row: (row.get("n_results") or 0) >= 1
            and (row.get("top_score") or 0) >= HIT_SCORE_MIN,
        ),
        "empty_rate": _frac(inv, lambda row: (row.get("n_results") or 0) == 0),
        "gap_rate": _frac(inv, lambda row: (row.get("coverage_gaps") or 0) >= 1),
        "stale_rate": _frac(inv, lambda row: (row.get("n_stale_indexes") or 0) >= 1),
        "median_duration_ms": statistics.median(durations) if durations else None,
        "json_flag_rate": _frac(inv, lambda row: bool(row.get("json_flag"))),
        "distinct_sessions": len(_sessions(inv)),
        "nudges_log_absent": nudges_log_absent,
        "nudge_firings": len(nudges),
        "nudge_conversion": conversion,
        "plans_citing_drive_paths": _plans_citing_drive_paths(repo_root, week),
        "malformed_lines": inv_malformed + nudge_malformed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate drive-index-search metrics for one ISO week.")
    parser.add_argument("--week", default=_iso_week(datetime.now(timezone.utc)), help="ISO week, e.g. 2026-W27")
    parser.add_argument("--metrics-dir", default=str(DEFAULT_METRICS_DIR))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)

    metrics_dir = Path(args.metrics_dir)
    agg = build_aggregate(metrics_dir, args.week, Path(args.repo_root))

    out_dir = metrics_dir / "weekly"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.week}-{agg['host']}.json"

    # Idempotent overwrite: if an existing aggregate matches on everything but
    # the generation timestamp, keep the existing bytes (re-runs are no-ops).
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if {k: v for k, v in existing.items() if k != "generated_at"} == {
                k: v for k, v in agg.items() if k != "generated_at"
            }:
                print(f"unchanged: {out_path}")
                _print_summary(agg)
                return 0
        except Exception:
            pass
    out_path.write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote: {out_path}")
    _print_summary(agg)
    return 0


def _print_summary(agg: dict) -> None:
    print(
        f"{agg['week']} @ {agg['host']}: {agg['invocations']} invocations, "
        f"hit_rate={agg['hit_rate']}, empty_rate={agg['empty_rate']}, "
        f"gap_rate={agg['gap_rate']}, stale_rate={agg['stale_rate']}, "
        f"median_duration_ms={agg['median_duration_ms']}, "
        f"nudges={agg['nudge_firings']}"
        f"{' (nudges.jsonl ABSENT)' if agg['nudges_log_absent'] else ''}, "
        f"conversion={agg['nudge_conversion']}, "
        f"plans_citing_drive_paths={agg['plans_citing_drive_paths']}, "
        f"malformed={agg['malformed_lines']}"
    )


if __name__ == "__main__":
    sys.exit(main())
