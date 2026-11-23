#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""gemini-usage.py — single source of truth for genuine Gemini (agy) usage LEFT.

agy persists no quota to disk (workspace-hub#3087). Genuine usage comes from two
free local signals; the MOST RECENT one wins:

  • MANUAL SNAPSHOT — the user's pasted /usage, captured by agy-usage-snapshot.py
    into ${AGY_USAGE_SNAPSHOT:-~/.cache/agy-usage-snapshot.json}. Carries % LEFT and
    a reset countdown for BOTH the weekly and 5-hour windows.
  • ACTIVE 429 — the gemini CLI writes ${GEMINI_ERROR_DIR:-/tmp}/gemini-client-error-*.json
    on exhaustion (filename = error time; body = "...reset after XhYmZs").

Precedence: if a 429 happened AFTER the last snapshot and its reset is still future,
the pool is exhausted now → 0% (this prevents a stale snapshot hiding a live throttle).
Otherwise use the snapshot's BINDING window (the one with least % left — that's the
real constraint), reporting its % LEFT and reset countdown. Else unavailable.

Prints ONE JSON line for the statusline + the agent-quota collector:
  {pct_remaining, hours_to_reset, window, captured_at, stale, source}

Env: AGY_USAGE_SNAPSHOT, GEMINI_ERROR_DIR, STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS (default 48).
"""
from __future__ import annotations

import glob
import json
import os
import re
from datetime import datetime, timezone

SNAPSHOT = os.environ.get("AGY_USAGE_SNAPSHOT", os.path.expanduser("~/.cache/agy-usage-snapshot.json"))
ERROR_DIR = os.environ.get("GEMINI_ERROR_DIR", "/tmp")
MAX_AGE_H = float(os.environ.get("STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS", "48"))

_DUR = re.compile(r"reset after\s+(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", re.I)
_TS = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})-(\d{3})Z")


def latest_429(now: float) -> tuple[float, float] | None:
    """(error_time_epoch, reset_epoch) of the most recent FUTURE-reset 429, or None."""
    best = None
    for path in glob.glob(os.path.join(ERROR_DIR, "gemini-client-error-*.json")):
        m = _TS.search(os.path.basename(path))
        if not m:
            continue
        try:
            ferr = datetime.fromisoformat(
                f"{m.group(1)}T{m.group(2)}:{m.group(3)}:{m.group(4)}.{m.group(5)}+00:00"
            ).timestamp()
        except ValueError:
            continue
        try:  # raw read — "reset after" text is nested (error.message / .stack)
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        dm = _DUR.search(body)
        if not dm or not any(dm.groups()):
            continue
        reset = ferr + int(dm.group(1) or 0) * 3600 + int(dm.group(2) or 0) * 60 + int(dm.group(3) or 0)
        if reset > now and (best is None or ferr > best[0]):
            best = (ferr, reset)
    return best


def _windows(gem: dict) -> dict:
    """Normalize gemini snapshot to {window: {pct_remaining, reset_hours}}, old-schema tolerant."""
    if not isinstance(gem, dict):
        return {}
    if "weekly" in gem and isinstance(gem["weekly"], dict):  # new nested schema
        return {k: v for k, v in gem.items() if isinstance(v, dict) and "pct_remaining" in v}
    # legacy flat schema: weekly_pct_avail / five_hour_pct_avail
    out = {}
    if gem.get("weekly_pct_avail") is not None:
        out["weekly"] = {"pct_remaining": gem["weekly_pct_avail"], "reset_hours": None}
    if gem.get("five_hour_pct_avail") is not None:
        out["five_hour"] = {"pct_remaining": gem["five_hour_pct_avail"], "reset_hours": None}
    return out


def main() -> int:
    now = datetime.now(timezone.utc).timestamp()
    out = {
        "pct_remaining": None, "hours_to_reset": None, "window": None,
        "captured_at": None, "stale": False, "source": "unavailable",
    }

    captured_epoch = None
    captured_str = None
    wins = {}
    if os.path.exists(SNAPSHOT):
        try:
            data = json.load(open(SNAPSHOT, encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if isinstance(data, dict):
            captured_str = data.get("captured_at")
            try:
                captured_epoch = datetime.fromisoformat(captured_str.replace("Z", "+00:00")).timestamp()
            except (AttributeError, ValueError):
                captured_epoch = None
            wins = _windows(data.get("gemini"))

    # A 429 newer than the snapshot (or no snapshot) and still in its reset window → throttled now.
    t = latest_429(now)
    if t is not None and (captured_epoch is None or t[0] > captured_epoch):
        out.update(
            pct_remaining=0, hours_to_reset=round((t[1] - now) / 3600, 1),
            window="five_hour", source="429-throttle",
        )
        print(json.dumps(out))
        return 0

    if wins:
        # Binding window = least % remaining (the real constraint); ties prefer weekly.
        order = {"weekly": 0, "five_hour": 1}
        name, w = min(wins.items(), key=lambda kv: (kv[1]["pct_remaining"], order.get(kv[0], 9)))
        stale = True if captured_epoch is None else (now - captured_epoch) / 3600 > MAX_AGE_H
        rh = w.get("reset_hours")
        out.update(
            pct_remaining=int(round(w["pct_remaining"])),
            hours_to_reset=(round(rh, 1) if rh is not None else None),
            window=name,
            captured_at=captured_str,
            stale=stale,
            source="manual-snapshot",
        )

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
