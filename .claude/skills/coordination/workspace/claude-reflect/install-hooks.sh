#!/usr/bin/env bash
# install-hooks.sh - Install session logging and correction hooks in any repo
# Usage: ./install-hooks.sh [target-repo-path]
#
# Installs:
# - session-logger.sh (captures ALL tool calls)
# - capture-corrections.sh (captures edit corrections)
# - Updates settings.json with Pre/PostToolUse hooks
#
# Platform: Linux, macOS, Windows (Git Bash/WSL)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-.}"
TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"

echo "Installing session logging hooks to: $TARGET_REPO"
echo ""

# Ensure target has .claude/hooks directory
mkdir -p "$TARGET_REPO/.claude/hooks"

# ============================================
# Install session-logger.sh
# ============================================
echo "→ Installing session-logger.sh..."

cp "$SCRIPT_DIR/../../../hooks/session-logger.sh" "$TARGET_REPO/.claude/hooks/" 2>/dev/null || \
cat > "$TARGET_REPO/.claude/hooks/session-logger.sh" << 'SESSION_HOOK_EOF'
#!/usr/bin/env bash
# session-logger.sh - Log ALL tool calls for session analysis
# Platform: Linux, macOS, Windows (Git Bash/WSL)
set -uo pipefail
[[ "${CLAUDE_SESSION_LOGGING:-true}" != "true" ]] && exit 0

# Cross-platform workspace detection
detect_workspace_hub() {
    [[ -n "${WORKSPACE_HUB:-}" ]] && echo "$WORKSPACE_HUB" && return
    case "$(uname -s)" in
        Linux*) for d in "/mnt/github/workspace-hub" "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        Darwin*) for d in "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        MINGW*|MSYS*|CYGWIN*) for d in "/c/github/workspace-hub" "/c/Users/$USER/github/workspace-hub" "$HOME/github/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
    esac
    echo "$HOME/.claude"
}

WORKSPACE_HUB="$(detect_workspace_hub)"
SESSIONS_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}/sessions"
mkdir -p "$SESSIONS_DIR" 2>/dev/null
SESSION_FILE="${SESSIONS_DIR}/session_$(date +%Y%m%d).jsonl"

INPUT=$(cat)
PHASE="${1:-unknown}"
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)
TIMESTAMP=$(date -Iseconds)
EPOCH=$(date +%s%3N 2>/dev/null || date +%s)000
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null | head -c 500)
REPO_CONTEXT=$(echo "$FILE_PATH" | sed -n 's|.*/workspace-hub/\([^/]*\)/.*|\1|p')
[[ -z "$REPO_CONTEXT" ]] && REPO_CONTEXT="workspace-hub"
SESSION_ID="${CLAUDE_SESSION_ID:-$(echo "$$-$(date +%Y%m%d)" | md5sum 2>/dev/null | cut -c1-8 || echo "$$")}"

if [[ "$PHASE" == "pre" ]]; then
    jq -cn --arg ts "$TIMESTAMP" --arg epoch "$EPOCH" --arg phase "pre" --arg tool "$TOOL_NAME" \
        --arg session "$SESSION_ID" --arg repo "$REPO_CONTEXT" --arg file "$FILE_PATH" --arg cmd "$COMMAND" \
        '{timestamp:$ts,epoch_ms:($epoch|tonumber),phase:$phase,session_id:$session,tool:$tool,repo:$repo,file:(if $file!="" then $file else null end),command:(if $cmd!="" then $cmd else null end)}' \
        >> "$SESSION_FILE" 2>/dev/null
elif [[ "$PHASE" == "post" ]]; then
    LAST_PRE=$(tail -20 "$SESSION_FILE" 2>/dev/null | jq -r "select(.tool==\"$TOOL_NAME\" and .phase==\"pre\") | .epoch_ms" 2>/dev/null | tail -1)
    DURATION=$([[ -n "$LAST_PRE" && "$LAST_PRE" != "null" ]] && echo $((EPOCH - LAST_PRE)) || echo 0)
    jq -cn --arg ts "$TIMESTAMP" --arg epoch "$EPOCH" --arg phase "post" --arg tool "$TOOL_NAME" \
        --arg session "$SESSION_ID" --arg repo "$REPO_CONTEXT" --arg file "$FILE_PATH" --argjson dur "$DURATION" \
        '{timestamp:$ts,epoch_ms:($epoch|tonumber),phase:$phase,session_id:$session,tool:$tool,repo:$repo,file:(if $file!="" then $file else null end),duration_ms:$dur}' \
        >> "$SESSION_FILE" 2>/dev/null
fi
exit 0
SESSION_HOOK_EOF

chmod +x "$TARGET_REPO/.claude/hooks/session-logger.sh"

# ============================================
# Install capture-corrections.sh
# ============================================
echo "→ Installing capture-corrections.sh..."

cp "$SCRIPT_DIR/../../../hooks/capture-corrections.sh" "$TARGET_REPO/.claude/hooks/" 2>/dev/null || \
cat > "$TARGET_REPO/.claude/hooks/capture-corrections.sh" << 'CORRECTIONS_HOOK_EOF'
#!/usr/bin/env bash
# capture-corrections.sh - Capture edit corrections for RAGS analysis
# Platform: Linux, macOS, Windows (Git Bash/WSL)
set -uo pipefail
[[ "${CLAUDE_CAPTURE_CORRECTIONS:-true}" != "true" ]] && exit 0

detect_workspace_hub() {
    [[ -n "${WORKSPACE_HUB:-}" ]] && echo "$WORKSPACE_HUB" && return
    case "$(uname -s)" in
        Linux*) for d in "/mnt/github/workspace-hub" "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        Darwin*) for d in "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        MINGW*|MSYS*|CYGWIN*) for d in "/c/github/workspace-hub" "/c/Users/$USER/github/workspace-hub" "$HOME/github/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
    esac
    echo "$HOME/.claude"
}

WORKSPACE_HUB="$(detect_workspace_hub)"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}/corrections"
mkdir -p "$STATE_DIR" 2>/dev/null
SESSION_FILE="${STATE_DIR}/session_$(date +%Y%m%d).jsonl"
RECENT_EDITS="${STATE_DIR}/.recent_edits"

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[[ -z "$FILE_PATH" ]] && exit 0
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "Edit"' 2>/dev/null)
TIMESTAMP=$(date -Iseconds)

IS_CORRECTION=false
CORRECTION_GAP=0
if [[ -f "$RECENT_EDITS" ]]; then
    LAST_EDIT=$(grep -F "$FILE_PATH" "$RECENT_EDITS" 2>/dev/null | tail -1)
    if [[ -n "$LAST_EDIT" ]]; then
        LAST_TS=$(echo "$LAST_EDIT" | cut -d'|' -f1)
        LAST_EPOCH=$(date -d "$LAST_TS" +%s 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        CORRECTION_GAP=$((NOW_EPOCH - LAST_EPOCH))
        [[ $CORRECTION_GAP -lt 600 && $CORRECTION_GAP -gt 0 ]] && IS_CORRECTION=true
    fi
fi

echo "${TIMESTAMP}|${FILE_PATH}" >> "$RECENT_EDITS"
[[ $(wc -l < "$RECENT_EDITS" 2>/dev/null || echo 0) -gt 50 ]] && \
    tail -n 50 "$RECENT_EDITS" > "${RECENT_EDITS}.tmp" && mv "${RECENT_EDITS}.tmp" "$RECENT_EDITS"

if [[ "$IS_CORRECTION" == "true" ]]; then
    jq -cn --arg ts "$TIMESTAMP" --arg file "$FILE_PATH" --arg tool "$TOOL_NAME" --argjson gap "$CORRECTION_GAP" \
        '{timestamp:$ts,file:$file,tool:$tool,correction_gap_seconds:$gap,type:"correction"}' \
        >> "$SESSION_FILE" 2>/dev/null
fi
exit 0
CORRECTIONS_HOOK_EOF

chmod +x "$TARGET_REPO/.claude/hooks/capture-corrections.sh"

# ============================================
# Update settings.json
# ============================================
echo "→ Configuring settings.json..."

SETTINGS_FILE="$TARGET_REPO/.claude/settings.json"

if [[ -f "$SETTINGS_FILE" ]]; then
    # Check if hooks already configured
    if grep -q "session-logger.sh" "$SETTINGS_FILE" 2>/dev/null; then
        echo "  Session hooks already configured"
    else
        echo "  Adding hooks to existing settings.json..."
        # Backup
        cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"

        # Add hooks using jq
        jq '
            .hooks.PreToolUse = [
                {
                    "matcher": ".*",
                    "hooks": [{"type": "command", "command": "cat | \"'"$TARGET_REPO"'/.claude/hooks/session-logger.sh\" pre"}]
                }
            ] + (.hooks.PreToolUse // []) |
            .hooks.PostToolUse = [
                {
                    "matcher": ".*",
                    "hooks": [{"type": "command", "command": "cat | \"'"$TARGET_REPO"'/.claude/hooks/session-logger.sh\" post"}]
                },
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [{"type": "command", "command": "cat | \"'"$TARGET_REPO"'/.claude/hooks/capture-corrections.sh\""}]
                }
            ] + (.hooks.PostToolUse // [])
        ' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
    fi
else
    echo "  Creating new settings.json..."
    cat > "$SETTINGS_FILE" << SETTINGS_EOF
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {"type": "command", "command": "cat | \"$TARGET_REPO/.claude/hooks/session-logger.sh\" pre"}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {"type": "command", "command": "cat | \"$TARGET_REPO/.claude/hooks/session-logger.sh\" post"}
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {"type": "command", "command": "cat | \"$TARGET_REPO/.claude/hooks/capture-corrections.sh\""}
        ]
      }
    ]
  }
}
SETTINGS_EOF
fi

echo ""
echo "✅ Session logging hooks installed!"
echo ""
echo "Captures:"
echo "  • ALL tool calls (Read, Write, Edit, Bash, Grep, etc.)"
echo "  • Edit corrections (re-edits within 10 min)"
echo "  • Tool duration and workflow patterns"
echo ""
echo "State saved to: workspace-hub/.claude/state/"
echo "  • sessions/session_YYYYMMDD.jsonl"
echo "  • corrections/session_YYYYMMDD.jsonl"
echo ""
echo "Note: Restart Claude Code session for hooks to take effect."
