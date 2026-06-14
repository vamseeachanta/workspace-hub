#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""agy-usage-snapshot.py — capture Antigravity (`agy`) /usage into a statusline-readable snapshot.

WHY: agy's real Gemini quota is server-fetched and shown ONLY in the interactive
`/usage` TUI — no subcommand, no JSON, no on-disk persistence (workspace-hub#3087).
So genuine usage is captured by the human reading `/usage` and feeding the text here.

The panel reports two model groups ("GEMINI MODELS", "CLAUDE AND GPT MODELS"),
each with a "Weekly Limit" and "Five Hour Limit". For each, the line under the bar
reads either:
    "100% remaining · Refreshes in 159h 32m"   (→ pct_remaining + reset countdown)
    "Quota available"                            (→ full / no countdown shown)
This captures BOTH the % AVAILABLE (left) and the reset countdown (days/hours-left).

USAGE:
  1. In agy:  /usage   → copy the whole panel text.
  2. uv run scripts/ai/assessment/agy-usage-snapshot.py   (paste, then Ctrl-D)
     or:  uv run scripts/ai/assessment/agy-usage-snapshot.py --file /tmp/usage.txt

Writes: ~/.cache/agy-usage-snapshot.json  (override with $AGY_USAGE_SNAPSHOT)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

SNAPSHOT_PATH = os.environ.get(
    "AGY_USAGE_SNAPSHOT", os.path.expanduser("~/.cache/agy-usage-snapshot.json")
)

GROUPS = {"gemini": "GEMINI MODELS", "claude_gpt": "CLAUDE AND GPT MODELS"}
WINDOWS = {"weekly": "WEEKLY LIMIT", "five_hour": "FIVE HOUR LIMIT"}

_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_REMAIN = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*remaining", re.I)
# "Refreshes in 159h 32m" / "in 3h 12m" / "in 45m" / "in 6d 4h" / "5h51m23s"
_RESET = re.compile(
    r"(?:refreshes\s+in|reset(?:s)?\s+(?:in|after))\s+"
    r"(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?",
    re.I,
)


def _reset_hours(text: str) -> float | None:
    m = _RESET.search(text)
    if not m or not any(m.groups()):
        return None
    d, h, mi, s = (int(g or 0) for g in m.groups())
    return round(d * 24 + h + mi / 60 + s / 3600, 2)


def parse_usage(text: str) -> dict:
    """{group: {window: {pct_remaining: float, reset_hours: float|None}}}."""
    lines = text.splitlines()
    header_idx: dict[str, int] = {}
    for key, hdr in GROUPS.items():
        for i, ln in enumerate(lines):
            if hdr.upper() in ln.upper():
                header_idx[key] = i
                break
    if not header_idx:
        return {}

    ordered = sorted(header_idx.items(), key=lambda kv: kv[1])
    result: dict[str, dict] = {}
    for n, (gkey, start) in enumerate(ordered):
        end = ordered[n + 1][1] if n + 1 < len(ordered) else len(lines)
        block = lines[start:end]
        # find each window header's line index within the block
        win_idx = {}
        for wk, wh in WINDOWS.items():
            for i, ln in enumerate(block):
                if wh in ln.upper():
                    win_idx[wk] = i
                    break
        gvals: dict[str, dict] = {}
        wins_ordered = sorted(win_idx.items(), key=lambda kv: kv[1])
        for j, (wk, wstart) in enumerate(wins_ordered):
            wend = wins_ordered[j + 1][1] if j + 1 < len(wins_ordered) else len(block)
            wblock = "\n".join(block[wstart:wend])
            # pct: prefer the labeled "X% remaining"; else first % (the bar).
            rm = _REMAIN.search(wblock)
            if rm:
                pct = float(rm.group(1))
            else:
                pm = _PCT.search(wblock)
                if not pm:
                    continue
                # "Quota available" with a full bar → treat bar % as remaining.
                pct = float(pm.group(1))
            gvals[wk] = {"pct_remaining": pct, "reset_hours": _reset_hours(wblock)}
        if gvals:
            result[gkey] = gvals
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture agy /usage into a statusline snapshot.")
    ap.add_argument("--file", help="read /usage text from a file instead of stdin")
    ap.add_argument("--now", help="ISO timestamp override (testing); default = now")
    args = ap.parse_args()

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    if not text.strip():
        print("error: no /usage text provided on stdin (or --file)", file=sys.stderr)
        return 2

    parsed = parse_usage(text)
    gem = parsed.get("gemini", {})
    if "weekly" not in gem:
        print(
            "error: could not find a GEMINI MODELS 'Weekly Limit' in the pasted text. "
            "Paste the full /usage panel.",
            file=sys.stderr,
        )
        return 1

    captured_at = args.now or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    snapshot = {"captured_at": captured_at, "source": "manual-snapshot", **parsed}

    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    tmp = SNAPSHOT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
        f.write("\n")
    os.replace(tmp, SNAPSHOT_PATH)

    def fmt(w):
        if not w:
            return "n/a"
        r = w.get("reset_hours")
        rs = "" if r is None else (f" · {r/24:.1f}d left" if r >= 24 else f" · {r:.1f}h left")
        return f"{w['pct_remaining']:.0f}% left{rs}"

    print(f"Captured agy usage @ {captured_at}")
    print(f"  Gemini   weekly: {fmt(gem.get('weekly'))}   5h: {fmt(gem.get('five_hour'))}")
    if "claude_gpt" in parsed:
        c = parsed["claude_gpt"]
        print(f"  Claude+GPT weekly: {fmt(c.get('weekly'))}   5h: {fmt(c.get('five_hour'))}")
    print(f"  → {SNAPSHOT_PATH}")
    print("Statusline G: now shows genuine weekly % LEFT + days-to-reset. Re-run after future /usage reads.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
