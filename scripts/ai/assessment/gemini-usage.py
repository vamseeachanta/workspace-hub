#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""gemini-usage.py — single source of truth for genuine Gemini (agy) usage.

agy persists no quota to disk (workspace-hub#3087), so genuine Gemini usage comes
from two free local signals, in precedence order:

  1. ACTIVE THROTTLE — on a 429 the gemini CLI writes
     ${GEMINI_ERROR_DIR:-/tmp}/gemini-client-error-*.json whose FILENAME carries
     the error time and whose body says "...reset after XhYmZs". The shared
     Google AI Pro Gemini pool (same quota agy draws on) is exhausted until then.
  2. MANUAL SNAPSHOT — the user's pasted /usage weekly % AVAILABLE, captured into
     ${AGY_USAGE_SNAPSHOT:-~/.cache/agy-usage-snapshot.json} by agy-usage-snapshot.py.
  3. UNAVAILABLE — no signal; surface null (never a fabricated estimate).

Prints ONE JSON line consumed by BOTH the statusline (.claude/statusline-command.sh)
and the agent-quota collector (scripts/ai/assessment/lib/providers.sh):

  {pct_remaining, five_hour_pct, hours_to_reset, resets_at, captured_at, stale, source}

Env: AGY_USAGE_SNAPSHOT, GEMINI_ERROR_DIR, STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS (default 48).
"""
from __future__ import annotations

import glob
import json
import os
import re
from datetime import datetime, timedelta, timezone

SNAPSHOT = os.environ.get("AGY_USAGE_SNAPSHOT", os.path.expanduser("~/.cache/agy-usage-snapshot.json"))
ERROR_DIR = os.environ.get("GEMINI_ERROR_DIR", "/tmp")
MAX_AGE_H = float(os.environ.get("STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS", "48"))

_DUR = re.compile(r"reset after\s+(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", re.I)
_TS = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})-(\d{3})Z")


def throttle_reset_epoch(now: float) -> float | None:
    """Latest FUTURE reset epoch across gemini CLI 429 error reports, or None."""
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
        if reset > now and (best is None or reset > best):
            best = reset
    return best


def main() -> int:
    now = datetime.now(timezone.utc).timestamp()
    out = {
        "pct_remaining": None, "five_hour_pct": None, "hours_to_reset": None,
        "resets_at": None, "captured_at": None, "stale": False, "source": "unavailable",
    }

    reset = throttle_reset_epoch(now)
    if reset is not None:
        out.update(
            pct_remaining=0,
            hours_to_reset=round((reset - now) / 3600, 1),
            resets_at=datetime.fromtimestamp(reset).astimezone().isoformat(timespec="seconds"),
            source="429-throttle",
        )
        print(json.dumps(out))
        return 0

    if os.path.exists(SNAPSHOT):
        try:
            data = json.load(open(SNAPSHOT, encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        gem = data.get("gemini") if isinstance(data, dict) else None
        wk = gem.get("weekly_pct_avail") if isinstance(gem, dict) else None
        if wk is not None:
            cap = data.get("captured_at")
            stale = True
            try:
                cap_epoch = datetime.fromisoformat(cap.replace("Z", "+00:00")).timestamp()
                stale = (now - cap_epoch) / 3600 > MAX_AGE_H
            except (AttributeError, ValueError):
                pass  # undatable = stale
            out.update(
                pct_remaining=int(wk),
                five_hour_pct=(int(gem["five_hour_pct_avail"]) if gem.get("five_hour_pct_avail") is not None else None),
                captured_at=cap,
                stale=stale,
                source="manual-snapshot",
            )

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
