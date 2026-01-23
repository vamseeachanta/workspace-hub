#!/usr/bin/env bash
# claude-with-logging.sh - Wrapper to run Claude with session capture
#
# Usage: ./claude-with-logging.sh [claude arguments...]
#
# Features:
# - Captures full session output to log file
# - Auto-extracts transcript for RAG on exit
# - Preserves all Claude functionality

WS="${WORKSPACE_HUB:-/d/workspace-hub}"
[ ! -d "$WS" ] && WS="/mnt/github/workspace-hub"

LOG_DIR="${WS}/.claude/skills/session-logs/raw"
mkdir -p "$LOG_DIR"

SESSION_TS=$(date +%Y%m%d_%H%M%S)
PROJECT=$(basename "$(pwd)")
RAW_LOG="${LOG_DIR}/${PROJECT}_${SESSION_TS}.log"

echo "Session logging to: $RAW_LOG"
echo "---"

# Run Claude with tee to capture output
# Use script command for full terminal capture if available
if command -v script &>/dev/null; then
    script -q -c "claude $*" "$RAW_LOG"
else
    claude "$@" 2>&1 | tee "$RAW_LOG"
fi

EXIT_CODE=$?

echo "---"
echo "Session saved to: $RAW_LOG"

# Extract transcript for RAG
EXTRACT_SCRIPT="${WS}/.claude/hooks/extract-session-for-rag.sh"
if [ -f "$EXTRACT_SCRIPT" ]; then
    echo "Extracting transcript for RAG..."
    source "$EXTRACT_SCRIPT" --current 2>/dev/null
fi

exit $EXIT_CODE
