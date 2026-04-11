#!/usr/bin/env bash
# session-governor-check.sh - PreToolUse hook for session governance enforcement
# Integrates session_governor.py check_session_limits() into Claude Code hooks.
# Issue: #1839 Phase 2b - Wire runtime enforcement into hooks
#
# Tracks tool calls per-session using $PPID as the session key. Each new
# Claude Code process gets a fresh counter — multi-session days no longer
# accumulate toward the ceiling.
#
# Below 80% of the governance ceiling, exits silently (fast path).
# At 80%+, delegates to session_governor.py for authoritative verdict.
# At the ceiling, emits a {"decision":"block"} to prevent further tool calls.
#
# Protocol: stdout JSON for Claude context, stderr for user terminal.
# Follows {"decision":"block","reason":"..."} convention (cross-review-gate.sh).
#
# Error tracking: consecutive error count is maintained by error-loop-tracker.sh
# (PostToolUse hook) in .claude/state/session-governor/consecutive-error-count.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
WS="${WORKSPACE_HUB:-$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
STATE_DIR="$WS/.claude/state/session-governor"
GOVERNOR="$WS/scripts/workflow/session_governor.py"

# Resolve Python interpreter portably (uv python find → python3 → python)
_UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""
[[ -z "$_UV_PY" ]] && _UV_PY=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)

# Session key: $PPID is the PID of the Claude Code process that invoked this hook.
# Each new Claude session is a new process — counter resets automatically.
SESSION_KEY="${PPID:-0}"
COUNTER_FILE="$STATE_DIR/tool-call-count-${SESSION_KEY}"

# 80% of the 1000-call threshold in governance-checkpoints.yaml
FAST_PATH_CEILING=800
THRESHOLD=1000

mkdir -p "$STATE_DIR" 2>/dev/null

# -- Clean up counter files from dead sessions (older than 7 days) --
find "$STATE_DIR" -name "tool-call-count-*" -mtime +7 -delete 2>/dev/null || true

# -- Increment per-session counter --
COUNT=0
if [[ -f "$COUNTER_FILE" ]]; then
  COUNT=$(cat "$COUNTER_FILE" 2>/dev/null) || COUNT=0
  [[ "$COUNT" =~ ^[0-9]+$ ]] || COUNT=0
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# -- Fast path: below warning zone --
if [[ $COUNT -lt $FAST_PATH_CEILING ]]; then
  exit 0
fi

# -- Read consecutive error count from error-loop-tracker.sh state --
CONSEC_ERRORS=0
ERROR_COUNT_FILE="$STATE_DIR/consecutive-error-count"
if [[ -f "$ERROR_COUNT_FILE" ]]; then
  CONSEC_ERRORS=$(cat "$ERROR_COUNT_FILE" 2>/dev/null) || CONSEC_ERRORS=0
  # Validate it's a number
  [[ "$CONSEC_ERRORS" =~ ^[0-9]+$ ]] || CONSEC_ERRORS=0
fi

# -- Delegate to session governor for authoritative verdict --
GOV_EXIT=0
if [[ -n "$_UV_PY" && -f "$GOVERNOR" ]]; then
  "$_UV_PY" "$GOVERNOR" --check-limits --tool-calls "$COUNT" --consecutive-errors "$CONSEC_ERRORS" > /dev/null 2>&1 || GOV_EXIT=$?
fi

case $GOV_EXIT in
  2) # STOP - governance ceiling reached, block further tool calls
    if [[ $CONSEC_ERRORS -ge 3 ]]; then
      echo "[session-governor] HARD STOP: ${CONSEC_ERRORS}x consecutive identical error - error loop detected." >&2
      echo "[session-governor] Do NOT retry. Escalate to user for diagnosis." >&2
      printf '{"decision":"block","reason":"Session governance HARD STOP: %d consecutive identical errors detected (error-loop-breaker threshold: 3). Stop retrying the same approach. Escalate to user. Run: uv run scripts/workflow/session_governor.py --check-limits --tool-calls %d --consecutive-errors %d"}\n' "$CONSEC_ERRORS" "$COUNT" "$CONSEC_ERRORS"
    else
      echo "[session-governor] HARD STOP: ${COUNT}/${THRESHOLD} tool calls - governance ceiling reached." >&2
      echo "[session-governor] Commit current work and end the session." >&2
      printf '{"decision":"block","reason":"Session governance HARD STOP: %d tool calls reached the %d-call ceiling (governance-checkpoints.yaml). Commit current work and end the session. Run: uv run scripts/workflow/session_governor.py --check-limits --tool-calls %d --consecutive-errors %d"}\n' "$COUNT" "$THRESHOLD" "$COUNT" "$CONSEC_ERRORS"
    fi
    exit 0
    ;;
  1) # PAUSE - warning zone, allow but warn
    if [[ $CONSEC_ERRORS -ge 2 ]]; then
      echo "[session-governor] WARNING: ${CONSEC_ERRORS}x consecutive identical error - approaching error loop threshold (3)." >&2
      echo "[session-governor] Consider a different approach before retrying." >&2
    else
      echo "[session-governor] WARNING: ${COUNT}/${THRESHOLD} tool calls - approaching governance ceiling." >&2
      echo "[session-governor] Consider wrapping up current work." >&2
    fi
    exit 0
    ;;
  *) # CONTINUE or governor unavailable - allow silently
    exit 0
    ;;
esac
