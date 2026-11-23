"""Fail-open invocation metrics for the drive-index-search CLI (#3340, epic #3333).

One emission point (called from search.py main()) captures ALL callers — skill,
plan-resource-intel, pre-calc, manual. Privacy by construction (plan D2):
- query is logged as a 12-hex sha256 truncation + token count, NEVER raw
  (opt-in raw logging for local tuning: DRIVE_SEARCH_LOG_RAW_QUERY=1)
- counts only for results/indexes/gaps — no paths, no per-result scores
- session join key (plan D3): --session flag > CLAUDE_CODE_SESSION_ID env > "unknown"
- n_stale_indexes derived from the envelope's `index_status` key (#3336);
  0 when the key is absent — forward-compatible (review r1 F2)

Fail-open discipline: a metrics bug must never break a search. Everything after
the opt-out check is wrapped; opt out entirely with DRIVE_SEARCH_NO_METRICS=1.

Log residency (plan D5): local gitignored JSONL at
data/drive-index-search/metrics/invocations.jsonl (override the metrics dir with
DRIVE_SEARCH_METRICS_DIR — used by tests and tuning runs). Weekly counts-only
aggregates are committed separately by aggregate_metrics.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_METRICS_DIR = REPO_ROOT / "data" / "drive-index-search" / "metrics"
LOG_FILENAME = "invocations.jsonl"

# Mirrors adapters.base.TOKEN_RE (kept local so metrics has zero import surface
# that could break a search).
_TOKEN_RE = re.compile(r"[A-Za-z0-9_./&+-]+")


def _metrics_dir() -> Path:
    override = os.environ.get("DRIVE_SEARCH_METRICS_DIR")
    return Path(override) if override else DEFAULT_METRICS_DIR


def emit_invocation(args, envelope, exit_code, t_start) -> None:
    """Append one JSONL metrics line. Never raises (fail-open)."""
    if os.environ.get("DRIVE_SEARCH_NO_METRICS") == "1":
        return
    try:
        query = getattr(args, "query", "") or ""
        session = (
            getattr(args, "session", None)
            or os.environ.get("CLAUDE_CODE_SESSION_ID")
            or "unknown"
        )
        env = envelope if isinstance(envelope, dict) else {}
        results = env.get("results") or []
        index_status = env.get("index_status") or []
        line = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": session,
            "caller": getattr(args, "caller", None) or "manual",
            "query_hash": hashlib.sha256(query.encode("utf-8")).hexdigest()[:12],
            "n_tokens": len(_TOKEN_RE.findall(query)),
            "n_results": len(results),
            "top_score": results[0].get("score") if results else None,
            "json_flag": bool(getattr(args, "as_json", False)),
            "indexes_queried": len(env.get("indexes_queried") or []),
            "coverage_gaps": len(env.get("coverage_gaps") or []),
            "n_stale_indexes": sum(
                1
                for status in index_status
                if isinstance(status, dict) and status.get("stale") is True
            ),
            "exit_code": exit_code,
            "duration_ms": int((time.monotonic() - t_start) * 1000),
        }
        if os.environ.get("DRIVE_SEARCH_LOG_RAW_QUERY") == "1":
            line["query_raw"] = query  # documented local-tuning opt-in ONLY
        metrics_dir = _metrics_dir()
        metrics_dir.mkdir(parents=True, exist_ok=True)
        with open(metrics_dir / LOG_FILENAME, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, sort_keys=True) + "\n")
    except Exception:
        pass  # fail-open: metrics never break a search
