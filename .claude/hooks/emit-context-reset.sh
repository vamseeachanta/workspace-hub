#!/usr/bin/env bash
# emit-context-reset.sh — Emit context_reset signal to session-signals/
# WRK-305: Signal 1 — /clear invocation event.
#
# WIRE-UP STATUS: PLACEHOLDER — /clear cannot be intercepted by Claude Code hooks.
# Call this script from a /clear skill wrapper once the skill is created.
# See .claude/docs/hooks/session-quality-signals.md for full wire-up instructions.
#
# Usage:
#   bash emit-context-reset.sh [session_id] [active-wrk]
#
# Or pipe Stop hook stdin:
#   cat | bash emit-context-reset.sh
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
SIGNAL_DIR="${WS}/.claude/state/session-signals"
mkdir -p "$SIGNAL_DIR"

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DATE=$(date +%Y-%m-%d)

# Accept session_id and wrk from args, or try stdin JSON, or fall back
SESSION_ID="${1:-}"
ACTIVE_WRK="${2:-none}"

if [[ -z "$SESSION_ID" && ! -t 0 ]]; then
    INPUT=$(cat 2>/dev/null) || INPUT=""
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null) || SESSION_ID="unknown"
fi
[[ -z "$SESSION_ID" ]] && SESSION_ID="unknown"

# Detect active WRK from work-queue/working/ if not provided
if [[ "$ACTIVE_WRK" == "none" && -d "${WS}/.claude/work-queue/working" ]]; then
    ACTIVE_WRK=$(find "${WS}/.claude/work-queue/working" -maxdepth 1 \
        -name "WRK-*.md" | head -1 \
        | xargs -I{} basename {} .md 2>/dev/null) || ACTIVE_WRK="none"
fi
[[ -z "$ACTIVE_WRK" ]] && ACTIVE_WRK="none"

ENTRY="{\"ts\":\"${TS}\",\"event\":\"context_reset\""
ENTRY="${ENTRY},\"session_id\":\"${SESSION_ID}\""
ENTRY="${ENTRY},\"wrk\":\"${ACTIVE_WRK}\"}"

echo "$ENTRY" >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl" 2>/dev/null

exit 0
