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

# 2. Read input from stdin
# The hook receives a JSON object with session metadata and events
INPUT=$(cat)
if [[ -z "$INPUT" ]]; then
    # Fallback for empty stdin: create a minimal stub
    INPUT="{\"session_id\": \"unknown-$(date +%s)\", \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}"
fi

# 3. Extract date for daily bucketing (YYYY-MM-DD)
# jq is required for extracting timestamp, fallback to current date if jq fails or field missing
LOG_DATE=$(echo "$INPUT" | jq -r '.timestamp' 2>/dev/null | cut -d'T' -f1)
if [[ -z "$LOG_DATE" || "$LOG_DATE" == "null" ]]; then
    LOG_DATE=$(date +%Y-%m-%d)
fi

# 4. Atomic append to daily signal file
SIGNAL_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"
mkdir -p "$SIGNAL_DIR" 2>/dev/null
echo "$INPUT" >> "${SIGNAL_DIR}/${LOG_DATE}.jsonl"

# Exit 0 regardless of minor errors to ensure session exit is not blocked
exit 0
