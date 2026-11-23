#!/usr/bin/env bash
# tool-call-ceiling.sh — PostToolUse hook to detect runaway sessions
# Issue: #1428 — Nyquist verification gates
#
# Counts tool calls in the current session and emits a warning when
# approaching the ceiling. Writes a BLOCK signal file when exceeded.
#
# The ceiling is advisory — Claude hooks cannot hard-kill a session,
# but the warning is injected into the assistant context to trigger
# graceful shutdown.
#
# Default ceiling: 500 tool calls per session.
# Override: TOOL_CALL_CEILING env var.

set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
SESSION_DIR="${WS}/.claude/state/sessions"
SIGNAL_DIR="${WS}/.claude/state/session-signals"
CEILING="${TOOL_CALL_CEILING:-500}"
WARN_AT=$(( CEILING * 80 / 100 ))  # Warn at 80%

mkdir -p "$SESSION_DIR" "$SIGNAL_DIR"

# Count today's tool calls from session log
TODAY_SESSION="${SESSION_DIR}/session_$(date +%Y%m%d).jsonl"
if [[ ! -f "$TODAY_SESSION" ]]; then
  exit 0
fi

CALL_COUNT=$(grep -c '"hook":"pre"' "$TODAY_SESSION" 2>/dev/null) || CALL_COUNT=0

# Below warning threshold — silent exit
if [[ $CALL_COUNT -lt $WARN_AT ]]; then
  exit 0
fi

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# At warning threshold — emit warning
if [[ $CALL_COUNT -ge $WARN_AT && $CALL_COUNT -lt $CEILING ]]; then
  REMAINING=$(( CEILING - CALL_COUNT ))
  echo "[tool-ceiling] WARNING: ${CALL_COUNT}/${CEILING} tool calls used. ${REMAINING} remaining." >&2
  echo "[tool-ceiling] Consider wrapping up or committing current work." >&2
  exit 0
fi

# At or above ceiling — emit block signal
echo "[tool-ceiling] CEILING REACHED: ${CALL_COUNT}/${CEILING} tool calls." >&2
echo "[tool-ceiling] Session should wrap up immediately to prevent runaway loops." >&2
echo "[tool-ceiling] Commit current work and end the session." >&2

# Log the ceiling breach as a session signal
LOG_DATE=$(date +%Y-%m-%d)
ENTRY="{\"ts\":\"${TS}\",\"event\":\"tool_call_ceiling_breach\",\"call_count\":${CALL_COUNT},\"ceiling\":${CEILING}}"
echo "$ENTRY" >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl" 2>/dev/null

exit 0
