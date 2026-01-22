#!/usr/bin/env bash
# install-hooks.sh - Install correction learning hooks in any repo
# Usage: ./install-hooks.sh [target-repo-path]
#
# Installs:
# - capture-corrections.sh hook
# - Updates settings.json with PostToolUse hook

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-.}"

echo "Installing correction learning hooks to: $TARGET_REPO"

# Ensure target has .claude directory
mkdir -p "$TARGET_REPO/.claude/hooks"

# Copy hook script
cp "$SCRIPT_DIR/../../../hooks/capture-corrections.sh" "$TARGET_REPO/.claude/hooks/" 2>/dev/null || \
cat > "$TARGET_REPO/.claude/hooks/capture-corrections.sh" << 'HOOK_EOF'
#!/usr/bin/env bash
# capture-corrections.sh - Lightweight hook to capture AI correction patterns
# All corrections saved to workspace-hub for unified RAGS analysis
set -uo pipefail
[[ "${CLAUDE_CAPTURE_CORRECTIONS:-true}" != "true" ]] && exit 0
# Central state: always save to workspace-hub for unified analysis
WORKSPACE_HUB="${WORKSPACE_HUB:-/mnt/github/workspace-hub}"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}/corrections"
SESSION_FILE="${STATE_DIR}/session_$(date +%Y%m%d).jsonl"
RECENT_EDITS="${STATE_DIR}/.recent_edits"
MAX_RECENT=50
mkdir -p "$STATE_DIR" 2>/dev/null
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
[[ $(wc -l < "$RECENT_EDITS" 2>/dev/null || echo 0) -gt $MAX_RECENT ]] && \
    tail -n $MAX_RECENT "$RECENT_EDITS" > "${RECENT_EDITS}.tmp" && mv "${RECENT_EDITS}.tmp" "$RECENT_EDITS"
if [[ "$IS_CORRECTION" == "true" ]]; then
    DIFF_STAT=""
    command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1 && \
        DIFF_STAT=$(git diff --stat "$FILE_PATH" 2>/dev/null | tail -1 || echo "")
    jq -cn --arg ts "$TIMESTAMP" --arg file "$FILE_PATH" --arg tool "$TOOL_NAME" \
        --argjson gap "$CORRECTION_GAP" --arg diff "$DIFF_STAT" \
        '{timestamp:$ts,file:$file,tool:$tool,correction_gap_seconds:$gap,diff_stat:$diff,type:"correction"}' \
        >> "$SESSION_FILE" 2>/dev/null
fi
exit 0
HOOK_EOF

chmod +x "$TARGET_REPO/.claude/hooks/capture-corrections.sh"

# Update settings.json if it exists
SETTINGS_FILE="$TARGET_REPO/.claude/settings.json"
if [[ -f "$SETTINGS_FILE" ]]; then
    # Check if hook already exists
    if grep -q "capture-corrections.sh" "$SETTINGS_FILE" 2>/dev/null; then
        echo "Hook already configured in settings.json"
    else
        echo "Adding hook to settings.json..."
        # Use jq to add the hook
        HOOK_CMD="cat | $TARGET_REPO/.claude/hooks/capture-corrections.sh"
        jq --arg cmd "$HOOK_CMD" '
            .hooks.PostToolUse[0].hooks += [{"type": "command", "command": $cmd}]
        ' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
    fi
else
    echo "No settings.json found - creating minimal config"
    cat > "$SETTINGS_FILE" << SETTINGS_EOF
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "cat | $TARGET_REPO/.claude/hooks/capture-corrections.sh"
          }
        ]
      }
    ]
  }
}
SETTINGS_EOF
fi

echo ""
echo "✅ Correction learning hooks installed!"
echo ""
echo "Note: Restart Claude Code session for hooks to take effect."
echo "Corrections will be stored in: ~/.claude/state/corrections/"
echo "RAGS loop will process them during daily-reflect.sh runs."
