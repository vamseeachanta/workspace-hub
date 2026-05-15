#!/usr/bin/env bash
# consume-signals.sh — Lean session signal capture
# Target: < 30 lines, < 1s execution.
# Contract: Writes JSON from stdin to .claude/state/session-signals/YYYY-MM-DD.jsonl
set -uo pipefail

# 1. Resolve workspace
if [[ -z "${WORKSPACE_HUB:-}" ]]; then
    # Fast path: script is in .claude/hooks/, hub is ../..
    WORKSPACE_HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)"
fi

# 2. Read a bounded prefix from stdin.
# Stop hooks may receive a full JSONL transcript. Slurping it can exceed Claude's
# 10s hook timeout and `.timestamp` over JSONL expands to thousands of lines.
INPUT_PREFIX=""
if [[ ! -t 0 ]]; then
    INPUT_PREFIX=$(head -c 65536 2>/dev/null || true)
fi
FIRST_LINE=$(printf '%s\n' "$INPUT_PREFIX" | sed -n '1p')

if printf '%s' "$FIRST_LINE" | jq -e 'type == "object"' >/dev/null 2>&1; then
    SESSION_ID=$(printf '%s' "$FIRST_LINE" | jq -r '.session_id // "unknown"' 2>/dev/null)
    TS=$(printf '%s' "$FIRST_LINE" | jq -r '.timestamp // .ts // empty' 2>/dev/null)
else
    SESSION_ID="unknown-$(date +%s)"
    TS=""
fi

if [[ -z "$TS" || "$TS" == "null" ]]; then
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# 3. Extract date for daily bucketing (YYYY-MM-DD)
LOG_DATE=$(printf '%s' "$TS" | cut -d'T' -f1)
if [[ ! "$LOG_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    LOG_DATE=$(date +%Y-%m-%d)
fi

# 4. Atomic append to daily signal file
SIGNAL_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"
mkdir -p "$SIGNAL_DIR" 2>/dev/null
jq -cn \
    --arg ts "$TS" \
    --arg session_id "$SESSION_ID" \
    --arg event "stop_signal_captured" \
    '{ts: $ts, event: $event, session_id: $session_id}' \
    >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl" 2>/dev/null || true

# Exit 0 regardless of minor errors to ensure session exit is not blocked
exit 0
