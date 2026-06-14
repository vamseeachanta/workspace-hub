#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""agy-usage-snapshot.py — capture Antigravity (`agy`) /usage into a statusline-readable snapshot.

WHY: agy's real Gemini quota is server-fetched into memory and shown ONLY in the
interactive `/usage` TUI — no subcommand, no JSON, no on-disk persistence (see
workspace-hub#3087). So genuine usage can only be captured by the human reading
`/usage` and feeding the text here. This writes a machine-local snapshot that
`.claude/statusline-command.sh` renders for the `G:` segment (weekly % + a
staleness `?`). The windows are ROLLING (Weekly + Five-Hour), so there is no
fixed reset to count down to — the snapshot's age is the planning signal.

USAGE:
  1. In agy:  /usage   → copy the whole panel text.
  2. Paste it into this script via stdin:
       uv run scripts/ai/assessment/agy-usage-snapshot.py <<'EOF'
       ...paste /usage output...
       EOF
     or:  pbpaste | uv run scripts/ai/assessment/agy-usage-snapshot.py
     or:  uv run scripts/ai/assessment/agy-usage-snapshot.py --file /tmp/usage.txt

Writes: ~/.cache/agy-usage-snapshot.json  (override with $AGY_USAGE_SNAPSHOT)

Parses the two model groups agy reports — "GEMINI MODELS" and
"CLAUDE AND GPT MODELS" — each with a "Weekly Limit" and "Five Hour Limit"
percentage (shown as % AVAILABLE / remaining).
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

# Group header -> snapshot key. Match is substring + case-insensitive.
GROUPS = {
    "gemini": "GEMINI MODELS",
    "claude_gpt": "CLAUDE AND GPT MODELS",
}
WINDOWS = {
    "weekly_pct_avail": "WEEKLY LIMIT",
    "five_hour_pct_avail": "FIVE HOUR LIMIT",
}
PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def parse_usage(text: str) -> dict:
    """Return {group_key: {window_key: float_pct}} parsed from /usage panel text.

    Walks lines tracking the current group header and current window header; the
    first percentage seen after a window header is that window's value.
    """
    lines = text.splitlines()
    # Locate each group's line range by its header.
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
        gvals: dict[str, float] = {}
        cur_window: str | None = None
        for ln in block:
            up = ln.upper()
            matched_window = next(
                (wk for wk, wh in WINDOWS.items() if wh in up), None
            )
            if matched_window:
                cur_window = matched_window
                # A percentage may sit on the same line as the header.
                m = PCT_RE.search(ln)
                if m:
                    gvals[cur_window] = float(m.group(1))
                    cur_window = None
                continue
            if cur_window:
                m = PCT_RE.search(ln)
                if m:
                    gvals[cur_window] = float(m.group(1))
                    cur_window = None
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
    if "gemini" not in parsed or "weekly_pct_avail" not in parsed.get("gemini", {}):
        print(
            "error: could not find a GEMINI MODELS 'Weekly Limit' percentage in the "
            "pasted text. Paste the full /usage panel.",
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

    g = parsed["gemini"]
    gw = g.get("weekly_pct_avail")
    g5 = g.get("five_hour_pct_avail")
    print(f"Captured agy usage @ {captured_at}")
    print(f"  Gemini   weekly={gw}% avail" + (f"  5h={g5}% avail" if g5 is not None else ""))
    if "claude_gpt" in parsed:
        c = parsed["claude_gpt"]
        print(f"  Claude+GPT weekly={c.get('weekly_pct_avail')}% avail  5h={c.get('five_hour_pct_avail')}% avail")
    print(f"  → {SNAPSHOT_PATH}")
    print("Statusline G: now shows this weekly %. Re-run after future /usage reads to refresh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
