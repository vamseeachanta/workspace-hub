#!/usr/bin/env bash
# session-logger.sh - Comprehensive session transcript logger
# Captures ALL tool calls for full session analysis
#
# Usage: Called via PreToolUse and PostToolUse hooks
# Storage: workspace-hub/.claude/state/sessions/
#
# Captures: Tool name, inputs, outputs, timestamps, duration
# Platform: Linux, macOS, Windows (Git Bash/WSL)

set -uo pipefail

# Fast exit if disabled
[[ "${CLAUDE_SESSION_LOGGING:-true}" != "true" ]] && exit 0

# Detect OS and set workspace hub path
detect_workspace_hub() {
    # Check explicit override first
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi

    # Detect OS
    case "$(uname -s)" in
        Linux*)
            # Linux or WSL
            if [[ -d "/mnt/github/workspace-hub" ]]; then
                echo "/mnt/github/workspace-hub"
            elif [[ -d "$HOME/github/workspace-hub" ]]; then
                echo "$HOME/github/workspace-hub"
            elif [[ -d "$HOME/workspace-hub" ]]; then
                echo "$HOME/workspace-hub"
            else
                echo "$HOME/.claude"
            fi
            ;;
        Darwin*)
            # macOS
            if [[ -d "$HOME/github/workspace-hub" ]]; then
                echo "$HOME/github/workspace-hub"
            elif [[ -d "$HOME/workspace-hub" ]]; then
                echo "$HOME/workspace-hub"
            else
                echo "$HOME/.claude"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Windows Git Bash / MSYS / Cygwin
            # Convert Windows paths if needed
            if [[ -d "/c/github/workspace-hub" ]]; then
                echo "/c/github/workspace-hub"
            elif [[ -d "/c/Users/$USER/github/workspace-hub" ]]; then
                echo "/c/Users/$USER/github/workspace-hub"
            elif [[ -d "$HOME/github/workspace-hub" ]]; then
                echo "$HOME/github/workspace-hub"
            else
                echo "$HOME/.claude"
            fi
            ;;
        *)
            # Fallback
            echo "$HOME/.claude"
            ;;
    esac
}

# Central state location (cross-platform)
WORKSPACE_HUB="$(detect_workspace_hub)"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}"
SESSIONS_DIR="${STATE_DIR}/sessions"
SESSION_DATE=$(date +%Y%m%d)
SESSION_FILE="${SESSIONS_DIR}/session_${SESSION_DATE}.jsonl"

# Create directory
mkdir -p "$SESSIONS_DIR" 2>/dev/null

# Read input from stdin (hook receives JSON)
INPUT=$(cat)

# Determine hook phase from argument
PHASE="${1:-unknown}"  # "pre" or "post"

# Extract tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)
TIMESTAMP=$(date -Iseconds)
EPOCH=$(date +%s%3N)  # Milliseconds for duration calc

# Extract tool input (truncate large inputs)
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}' 2>/dev/null | head -c 2000)

# For file operations, extract key info
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null | head -c 500)

# Detect repo context from file path
REPO_CONTEXT=""
if [[ -n "$FILE_PATH" ]]; then
    # Extract repo name from path like /mnt/github/workspace-hub/digitalmodel/...
    REPO_CONTEXT=$(echo "$FILE_PATH" | sed -n 's|.*/workspace-hub/\([^/]*\)/.*|\1|p')
    [[ -z "$REPO_CONTEXT" ]] && REPO_CONTEXT="workspace-hub"
fi

# Session ID (persistent for the day, changes on new terminal)
SESSION_ID="${CLAUDE_SESSION_ID:-$(echo "$$-$SESSION_DATE" | md5sum | cut -c1-8)}"

# Build log entry
if [[ "$PHASE" == "pre" ]]; then
    # Pre-tool: Log intent
    jq -cn \
        --arg ts "$TIMESTAMP" \
        --arg epoch "$EPOCH" \
        --arg phase "pre" \
        --arg tool "$TOOL_NAME" \
        --arg session "$SESSION_ID" \
        --arg repo "$REPO_CONTEXT" \
        --arg file "$FILE_PATH" \
        --arg cmd "$COMMAND" \
        --argjson input "$TOOL_INPUT" \
        '{
            timestamp: $ts,
            epoch_ms: ($epoch | tonumber),
            phase: $phase,
            session_id: $session,
            tool: $tool,
            repo: $repo,
            file: (if $file != "" then $file else null end),
            command: (if $cmd != "" then $cmd else null end),
            input: $input
        }' >> "$SESSION_FILE" 2>/dev/null

elif [[ "$PHASE" == "post" ]]; then
    # Post-tool: Log completion with duration
    # Try to find matching pre entry for duration calc
    LAST_PRE_EPOCH=$(tail -20 "$SESSION_FILE" 2>/dev/null | \
        jq -r "select(.tool == \"$TOOL_NAME\" and .phase == \"pre\") | .epoch_ms" 2>/dev/null | tail -1)

    DURATION_MS=0
    if [[ -n "$LAST_PRE_EPOCH" && "$LAST_PRE_EPOCH" != "null" ]]; then
        DURATION_MS=$((EPOCH - LAST_PRE_EPOCH))
    fi

    jq -cn \
        --arg ts "$TIMESTAMP" \
        --arg epoch "$EPOCH" \
        --arg phase "post" \
        --arg tool "$TOOL_NAME" \
        --arg session "$SESSION_ID" \
        --arg repo "$REPO_CONTEXT" \
        --arg file "$FILE_PATH" \
        --argjson duration "$DURATION_MS" \
        '{
            timestamp: $ts,
            epoch_ms: ($epoch | tonumber),
            phase: $phase,
            session_id: $session,
            tool: $tool,
            repo: $repo,
            file: (if $file != "" then $file else null end),
            duration_ms: $duration
        }' >> "$SESSION_FILE" 2>/dev/null
fi

exit 0
