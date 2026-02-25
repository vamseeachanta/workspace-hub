#!/usr/bin/env bash
# session-logger.sh - Capture session activity for RAGS analysis
# Writes to: .claude/state/sessions/ (read by analyze-sessions.sh)

# Exit early if disabled
[ "${CLAUDE_SESSION_LOGGING:-true}" != "true" ] && exit 0

# Detect workspace hub
WS="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Write to state/sessions for RAGS analysis pipeline
LOG_DIR="${WS}/.claude/state/sessions"
LOG_FILE="${LOG_DIR}/session_$(date +%Y%m%d).jsonl"
HOOK_TYPE="${1:-pre}"

# Ensure dir exists
mkdir -p "$LOG_DIR" 2>/dev/null

# Read stdin if available (non-blocking)
INPUT="{}"
if [ ! -t 0 ]; then
    read -r -t 1 INPUT 2>/dev/null || INPUT="{}"
fi

# Parse JSON fields from tool input
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null) || TOOL="unknown"
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null) || FILE=""
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null | head -c 150) || CMD=""

# Get context
TS=$(date -Iseconds)
EPOCH=$(date +%s)
PROJ=$(basename "$(pwd)")
REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null) || REPO="$PROJ"

# Build log entry
ENTRY="{\"ts\":\"${TS}\",\"epoch\":${EPOCH},\"hook\":\"${HOOK_TYPE}\",\"tool\":\"${TOOL}\",\"project\":\"${PROJ}\",\"repo\":\"${REPO}\""
[ -n "$FILE" ] && ENTRY="${ENTRY},\"file\":\"${FILE}\""
[ -n "$CMD" ] && ENTRY="${ENTRY},\"cmd\":\"${CMD}\""
ENTRY="${ENTRY}}"

echo "$ENTRY" >> "$LOG_FILE" 2>/dev/null

exit 0
