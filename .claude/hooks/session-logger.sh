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
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null) || SESSION_ID=""

# Get context
TS=$(date -Iseconds)
EPOCH=$(date +%s)
PROJ=$(basename "$(pwd)")
REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null) || REPO="$PROJ"

# Build log entry — use jq to properly encode strings (handles quotes, newlines, etc.)
ENTRY=$(jq -cn \
  --arg ts "$TS" \
  --argjson epoch "$EPOCH" \
  --arg hook "$HOOK_TYPE" \
  --arg tool "$TOOL" \
  --arg project "$PROJ" \
  --arg repo "$REPO" \
  --arg file "${FILE:-}" \
  --arg cmd "${CMD:-}" \
  --arg session_id "${SESSION_ID:-}" \
  '{ts:$ts, epoch:$epoch, hook:$hook, tool:$tool, project:$project, repo:$repo}
   + if ($file != "") then {file:$file} else {} end
   + if ($cmd != "") then {cmd:$cmd} else {} end
   + if ($session_id != "") then {session_id:$session_id} else {} end' \
  2>/dev/null) \
  || ENTRY="{\"ts\":\"${TS}\",\"hook\":\"${HOOK_TYPE}\",\"tool\":\"${TOOL}\"}"

# Emit session_params on first write of the daily log
if [ ! -s "$LOG_FILE" ]; then
    PARAMS_SCRIPT="${WS}/scripts/ai/session-params.py"
    if [ -f "$PARAMS_SCRIPT" ]; then
        # Use uv python find to get absolute Python path (avoids uv run --no-project hang on Windows)
        _UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""
        PARAMS=$([ -n "$_UV_PY" ] && "$_UV_PY" "$PARAMS_SCRIPT" 2>/dev/null) || PARAMS=""
        if [ -n "$PARAMS" ]; then
            echo "$PARAMS" >> "$LOG_FILE" 2>/dev/null || true
        fi
    fi
fi

echo "$ENTRY" >> "$LOG_FILE" 2>/dev/null

# Dual-write: also append to unified orchestrator log
( mkdir -p "${WS}/logs/orchestrator/claude" \
  && echo "$ENTRY" >> "${WS}/logs/orchestrator/claude/session_$(date +%Y%m%d).jsonl" \
) 2>/dev/null || true

exit 0
