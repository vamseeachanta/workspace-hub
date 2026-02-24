#!/usr/bin/env bash
# emit-plan-mode-signal.sh — Emit plan_mode_start/end signal to session-signals/
# WRK-305: Signal 2 — plan-mode transition events.
#
# WIRE-UP STATUS: PLACEHOLDER — plan-mode transitions are not interceptable
# via current Claude Code hook events (PreToolUse, PostToolUse, PreCompact, Stop).
# See .claude/docs/hooks/session-quality-signals.md for future wire-up instructions.
#
# Usage:
#   bash emit-plan-mode-signal.sh start [session_id] [active-wrk]
#   bash emit-plan-mode-signal.sh end   [session_id] [active-wrk] [approved]
#
# Arguments:
#   $1  mode    — "start" or "end" (required)
#   $2  session_id — session UUID (optional, defaults to "unknown")
#   $3  wrk     — active WRK item ID, e.g. "WRK-305" (optional)
#   $4  approved — "true"/"false" for end events (optional, default "false")
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
SIGNAL_DIR="${WS}/.claude/state/session-signals"
mkdir -p "$SIGNAL_DIR"

MODE="${1:-start}"
SESSION_ID="${2:-unknown}"
ACTIVE_WRK="${3:-none}"
APPROVED="${4:-false}"

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DATE=$(date +%Y-%m-%d)

# Detect active WRK from work-queue/working/ if not provided
if [[ "$ACTIVE_WRK" == "none" && -d "${WS}/.claude/work-queue/working" ]]; then
    ACTIVE_WRK=$(find "${WS}/.claude/work-queue/working" -maxdepth 1 \
        -name "WRK-*.md" | head -1 \
        | xargs -I{} basename {} .md 2>/dev/null) || ACTIVE_WRK="none"
fi
[[ -z "$ACTIVE_WRK" ]] && ACTIVE_WRK="none"

if [[ "$MODE" == "start" ]]; then
    EVENT="plan_mode_start"
    ENTRY="{\"ts\":\"${TS}\",\"event\":\"${EVENT}\""
    ENTRY="${ENTRY},\"session_id\":\"${SESSION_ID}\""
    ENTRY="${ENTRY},\"wrk\":\"${ACTIVE_WRK}\"}"
else
    EVENT="plan_mode_end"
    ENTRY="{\"ts\":\"${TS}\",\"event\":\"${EVENT}\""
    ENTRY="${ENTRY},\"session_id\":\"${SESSION_ID}\""
    ENTRY="${ENTRY},\"wrk\":\"${ACTIVE_WRK}\""
    ENTRY="${ENTRY},\"approved\":${APPROVED}}"
fi

echo "$ENTRY" >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl" 2>/dev/null

exit 0
