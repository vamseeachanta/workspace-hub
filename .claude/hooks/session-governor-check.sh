#!/usr/bin/env bash
# session-governor-check.sh - PreToolUse hook for session governance enforcement
# Integrates session_governor.py check_session_limits() into Claude Code hooks.
# Issue: #1839 Phase 2b - Wire runtime enforcement into hooks
#
# Maintains a per-day tool call counter in .claude/state/session-governor/.
# Below 80% of the governance ceiling (160/200), exits silently (fast path).
# At 80%+, delegates to session_governor.py for authoritative verdict.
# At the ceiling, emits a {"decision":"block"} to prevent further tool calls.
#
# Protocol: stdout JSON for Claude context, stderr for user terminal.
# Follows {"decision":"block","reason":"..."} convention (cross-review-gate.sh).
#
# Gaps documented in SESSION-GOVERNANCE.md:
#   - consecutive-error tracking not yet wired (passes 0)
#   - counter resets daily, not per-session (no reliable session ID in hook env)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
WS="${WORKSPACE_HUB:-$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
STATE_DIR="$WS/.claude/state/session-governor"
COUNTER_FILE="$STATE_DIR/tool-call-count"
DATE_FILE="$STATE_DIR/counter-date"
GOVERNOR="$WS/scripts/workflow/session_governor.py"

# 80% of 200 threshold from governance-checkpoints.yaml
FAST_PATH_CEILING=160

mkdir -p "$STATE_DIR" 2>/dev/null

# -- Reset counter on new day --
TODAY=$(date +%Y%m%d)
if [[ -f "$DATE_FILE" ]]; then
  STORED_DATE=$(cat "$DATE_FILE" 2>/dev/null) || STORED_DATE=""
  if [[ "$STORED_DATE" != "$TODAY" ]]; then
    echo "0" > "$COUNTER_FILE"
    echo "$TODAY" > "$DATE_FILE"
  fi
else
  echo "$TODAY" > "$DATE_FILE"
fi

# -- Increment counter --
COUNT=0
if [[ -f "$COUNTER_FILE" ]]; then
  COUNT=$(cat "$COUNTER_FILE" 2>/dev/null) || COUNT=0
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# -- Fast path: below warning zone --
if [[ $COUNT -lt $FAST_PATH_CEILING ]]; then
  exit 0
fi

# -- Delegate to session governor for authoritative verdict --
# consecutive-errors: 0 until error-tracking pipeline is wired (#1839 Phase 3)
GOV_EXIT=0
uv run "$GOVERNOR" --check-limits --tool-calls "$COUNT" --consecutive-errors 0 > /dev/null 2>&1 || GOV_EXIT=$?

case $GOV_EXIT in
  2) # STOP - governance ceiling reached, block further tool calls
    echo "[session-governor] HARD STOP: ${COUNT}/200 tool calls - governance ceiling reached." >&2
    echo "[session-governor] Commit current work and end the session." >&2
    printf '{"decision":"block","reason":"Session governance HARD STOP: %d tool calls reached the 200-call ceiling (governance-checkpoints.yaml). Commit current work and end the session. Run: uv run scripts/workflow/session_governor.py --check-limits --tool-calls %d"}\n' "$COUNT" "$COUNT"
    exit 0
    ;;
  1) # PAUSE - warning zone, allow but warn
    echo "[session-governor] WARNING: ${COUNT}/200 tool calls - approaching governance ceiling." >&2
    echo "[session-governor] Consider wrapping up current work." >&2
    exit 0
    ;;
  *) # CONTINUE or governor unavailable - allow silently
    exit 0
    ;;
esac
