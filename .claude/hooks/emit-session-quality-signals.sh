#!/usr/bin/env bash
# emit-session-quality-signals.sh — Stop-time session quality signal emitter
# WRK-305: Wire session-quality signals for comprehensive-learning Phase 1.
#
# Emits to .claude/state/session-signals/YYYY-MM-DD.jsonl:
#   session_tool_summary — per-WRK tool-call counts (edits, reads, total)
#
# Called by Stop hook in settings.json. Must complete in < 1s.
# Reads session JSONL written by session-logger.sh (pre/post hook pairs).
#
# /clear and plan-mode signals are NOT interceptable via hooks.
# See .claude/docs/hooks/session-quality-signals.md for future wire-up.
set -uo pipefail

# Resolve workspace hub path
WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
SIGNAL_DIR="${WS}/.claude/state/session-signals"
SESSION_DIR="${WS}/.claude/state/sessions"
mkdir -p "$SIGNAL_DIR"

# Read only a bounded prefix from Stop-hook stdin. On large transcript payloads,
# reading all stdin just to extract session_id can exceed the 10s hook timeout.
INPUT_PREFIX=""
if [ ! -t 0 ]; then
    INPUT_PREFIX=$(head -c 65536 2>/dev/null || true)
fi
FIRST_LINE=$(printf '%s\n' "$INPUT_PREFIX" | sed -n '1p')
SESSION_ID=$(printf '%s' "$FIRST_LINE" | jq -r '.session_id // "unknown"' 2>/dev/null) || SESSION_ID="unknown"

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DATE=$(date +%Y-%m-%d)
TODAY_SESSION="${SESSION_DIR}/session_$(date +%Y%m%d).jsonl"

# Bail fast if no session file exists for today
if [[ ! -f "$TODAY_SESSION" ]]; then
    exit 0
fi

# Active work context (GSD workflow or none)
ACTIVE_WRK="none"

# Count tool calls in today's session JSONL by type
# session-logger.sh writes: {"ts":...,"hook":"pre"/"post","tool":"<name>",...}
TOTAL=$(grep -c '"hook":"pre"' "$TODAY_SESSION" 2>/dev/null) || TOTAL=0
EDITS=$(grep -c '"tool":"Write"\|"tool":"Edit"\|"tool":"MultiEdit"' "$TODAY_SESSION" 2>/dev/null) || EDITS=0
READS=$(grep -c '"tool":"Read"\|"tool":"Glob"\|"tool":"Grep"' "$TODAY_SESSION" 2>/dev/null) || READS=0

# Emit session_tool_summary signal
ENTRY="{\"ts\":\"${TS}\",\"event\":\"session_tool_summary\""
ENTRY="${ENTRY},\"session_id\":\"${SESSION_ID}\""
ENTRY="${ENTRY},\"wrk\":\"${ACTIVE_WRK}\""
ENTRY="${ENTRY},\"tool_calls\":${TOTAL}"
ENTRY="${ENTRY},\"edits\":${EDITS}"
ENTRY="${ENTRY},\"reads\":${READS}}"

echo "$ENTRY" >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl" 2>/dev/null

exit 0
