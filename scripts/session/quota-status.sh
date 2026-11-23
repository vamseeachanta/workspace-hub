#!/usr/bin/env bash
# quota-status.sh — Display AI provider quota utilization with threshold alerts.
# Reads config/ai-tools/agent-quota-latest.json and prints lines when thresholds trigger.
# Always exits 0 (informational, non-blocking).
# Usage: quota-status.sh [--json-path <path>]
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
JSON_PATH="${REPO_ROOT}/config/ai-tools/agent-quota-latest.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json-path) JSON_PATH="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Non-blocking: missing file → silent
[[ -f "$JSON_PATH" ]] || exit 0

# Stale check: warn if mtime > 4 hours
if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
  PY=$(command -v python3 2>/dev/null || command -v python)
  STALE=$(uv run --no-project python -c "
import os, time, sys
mtime = os.path.getmtime(sys.argv[1])
age_h = (time.time() - mtime) / 3600
print('yes' if age_h > 4 else 'no')
" "$JSON_PATH" 2>/dev/null) || STALE="no"
  [[ "$STALE" == "yes" ]] && echo "NOTE: quota data may be stale (>4h old)"
fi

# Parse and output per-provider status
uv run --no-project python - "$JSON_PATH" << 'PYEOF'
import json, sys

path = sys.argv[1]
try:
    data = json.loads(open(path).read())
except Exception:
    sys.exit(0)

agents = data.get("agents", [])

for agent in agents:
    provider = agent.get("provider", "?")
    week_pct = agent.get("week_pct")
    pct_remaining = agent.get("pct_remaining")
    source = agent.get("source", "")

    # Normalize to utilization (% used)
    if week_pct is not None:
        utilization = week_pct
    elif pct_remaining is not None:
        utilization = 100 - pct_remaining
    else:
        print(f"NOTE [{provider}]: quota data unavailable (source: {source})")
        continue

    # Clamp to valid range
    utilization = max(0, min(100, utilization))

    if utilization >= 90:
        print(f"WARN [{provider}]: {utilization:.0f}% used — route tasks to alternative provider")
    elif utilization >= 70:
        print(f"NOTE [{provider}]: {utilization:.0f}% used — approaching limit")
    # < 70: silent
PYEOF
exit 0
