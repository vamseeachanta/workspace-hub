#!/usr/bin/env bash
# capture-corrections.sh - Lightweight hook to capture AI correction patterns
# Runs as PostToolUse hook - async, non-blocking
#
# Impact: ~20-50ms per edit, runs in background
# Storage: $WORKSPACE_STATE_DIR/corrections/ (defaults to workspace-hub)
# Platform: Linux, macOS, Windows (Git Bash/WSL)
#
# Config: Set WORKSPACE_STATE_DIR to override state location

set -uo pipefail

# Fast exit if not enabled
[[ "${CLAUDE_CAPTURE_CORRECTIONS:-true}" != "true" ]] && exit 0

# Detect OS and set workspace hub path
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    case "$(uname -s)" in
        Linux*)
            for dir in "/mnt/github/workspace-hub" "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
        Darwin*)
            for dir in "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
        MINGW*|MSYS*|CYGWIN*)
            for dir in "/c/github/workspace-hub" "/c/Users/$USER/github/workspace-hub" "$HOME/github/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
    esac
    echo "$HOME/.claude"
}

# Central state: always save to workspace-hub for unified RAGS analysis
WORKSPACE_HUB="$(detect_workspace_hub)"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}/corrections"
SESSION_FILE="${STATE_DIR}/session_$(date +%Y%m%d).jsonl"
RECENT_EDITS="${STATE_DIR}/.recent_edits"
MAX_RECENT=50

# Ensure directories exist (fast, cached by OS)
mkdir -p "$STATE_DIR" 2>/dev/null

# Read input from stdin (hook receives JSON)
INPUT=$(cat)

# Extract fields (single jq parse for performance)
eval $(echo "$INPUT" | jq -r '
  @sh "FILE_PATH=\(.tool_input.file_path // "")",
  @sh "TOOL_NAME=\(.tool_name // "Edit")",
  @sh "OLD_STRING=\(.tool_input.old_string // "" | .[0:100])",
  @sh "NEW_STRING=\(.tool_input.new_string // "" | .[0:100])",
  @sh "WRITE_CONTENT=\(.tool_input.content // "" | .[0:100])"
' 2>/dev/null) || true
[[ -z "$FILE_PATH" ]] && exit 0

TIMESTAMP=$(date -Iseconds)
FILE_BASENAME=$(basename "$FILE_PATH")
FILE_EXTENSION="${FILE_BASENAME##*.}"
[[ "$FILE_EXTENSION" == "$FILE_BASENAME" ]] && FILE_EXTENSION="none"

# Increment edit sequence counter
SEQ_FILE="${STATE_DIR}/.edit_sequence_counter"
if [[ -f "$SEQ_FILE" ]]; then
    EDIT_SEQ=$(( $(cat "$SEQ_FILE") + 1 ))
else
    EDIT_SEQ=1
fi
echo "$EDIT_SEQ" > "$SEQ_FILE"

# Check if this is a correction (re-edit of recent file)
IS_CORRECTION=false
CORRECTION_GAP=0

if [[ -f "$RECENT_EDITS" ]]; then
    # Look for same file edited recently
    LAST_EDIT=$(grep -F "$FILE_PATH" "$RECENT_EDITS" 2>/dev/null | tail -1)
    if [[ -n "$LAST_EDIT" ]]; then
        LAST_TS=$(echo "$LAST_EDIT" | cut -d'|' -f1)
        LAST_EPOCH=$(date -d "$LAST_TS" +%s 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        CORRECTION_GAP=$((NOW_EPOCH - LAST_EPOCH))

        # If same file edited within 10 minutes, likely a correction
        if [[ $CORRECTION_GAP -lt 600 && $CORRECTION_GAP -gt 0 ]]; then
            IS_CORRECTION=true
        fi
    fi
fi

# Log the edit
echo "${TIMESTAMP}|${FILE_PATH}|${EDIT_SEQ}" >> "$RECENT_EDITS"

# Keep recent edits file small
if [[ $(wc -l < "$RECENT_EDITS" 2>/dev/null || echo 0) -gt $MAX_RECENT ]]; then
    tail -n $MAX_RECENT "$RECENT_EDITS" > "${RECENT_EDITS}.tmp" && mv "${RECENT_EDITS}.tmp" "$RECENT_EDITS"
fi

# If this is a correction, capture it for RAGS
if [[ "$IS_CORRECTION" == "true" ]]; then
    # Get git diff context if available
    DIFF_STAT=""
    if command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1; then
        DIFF_STAT=$(git diff --stat "$FILE_PATH" 2>/dev/null | tail -1 || echo "")
    fi

    # Build edit context
    if [[ "$TOOL_NAME" == "Write" ]]; then
        EDIT_OLD_PREVIEW=""
        EDIT_NEW_PREVIEW="$WRITE_CONTENT"
    else
        EDIT_OLD_PREVIEW="$OLD_STRING"
        EDIT_NEW_PREVIEW="$NEW_STRING"
    fi

    # Build chain from recent edits within 600s window
    CHAIN_FILES=()
    CHAIN_POSITIONS=()
    if [[ -f "$RECENT_EDITS" ]]; then
        while IFS='|' read -r ts fp seq; do
            # Handle old format without sequence_id
            [[ -z "$fp" ]] && continue
            EDIT_EPOCH=$(date -d "$ts" +%s 2>/dev/null || echo 0)
            GAP=$((NOW_EPOCH - EDIT_EPOCH))
            if [[ $GAP -ge 0 && $GAP -lt 600 ]]; then
                # Add unique files to chain
                local_found=false
                for cf in "${CHAIN_FILES[@]+"${CHAIN_FILES[@]}"}"; do
                    [[ "$cf" == "$fp" ]] && local_found=true && break
                done
                [[ "$local_found" == "false" ]] && CHAIN_FILES+=("$fp")
            fi
        done < "$RECENT_EDITS"
    fi
    CHAIN_LEN=${#CHAIN_FILES[@]}

    # Generate chain_id if chain has multiple edits
    if [[ $CHAIN_LEN -gt 0 ]]; then
        DATE_PREFIX=$(date +%Y%m%d)
        if command -v md5sum &>/dev/null; then
            CHAIN_HASH=$(echo "${CHAIN_FILES[*]}" | md5sum | cut -c1-8)
        elif command -v shasum &>/dev/null; then
            CHAIN_HASH=$(echo "${CHAIN_FILES[*]}" | shasum -a 256 | cut -c1-8)
        else
            CHAIN_HASH=$(printf '%04x%04x' $RANDOM $RANDOM)
        fi
        CHAIN_ID="${DATE_PREFIX}_${CHAIN_HASH}"
    else
        CHAIN_ID=""
    fi

    # Convert chain files to JSON array
    CHAIN_FILES_JSON="[]"
    if [[ $CHAIN_LEN -gt 0 ]]; then
        CHAIN_FILES_JSON=$(printf '%s\n' "${CHAIN_FILES[@]}" | jq -R . | jq -s .)
    fi

    # Append to session corrections log (JSONL format for easy processing)
    jq -cn \
        --arg ts "$TIMESTAMP" \
        --arg file "$FILE_PATH" \
        --arg basename "$FILE_BASENAME" \
        --arg tool "$TOOL_NAME" \
        --argjson gap "$CORRECTION_GAP" \
        --arg diff "$DIFF_STAT" \
        --arg ext "$FILE_EXTENSION" \
        --arg old_preview "$EDIT_OLD_PREVIEW" \
        --arg new_preview "$EDIT_NEW_PREVIEW" \
        --arg chain_id "$CHAIN_ID" \
        --argjson chain_pos "$((CHAIN_LEN))" \
        --argjson chain_files "$CHAIN_FILES_JSON" \
        --argjson seq "$EDIT_SEQ" \
        '{
            timestamp: $ts,
            file: $file,
            basename: $basename,
            tool: $tool,
            correction_gap_seconds: $gap,
            diff_stat: $diff,
            type: "correction",
            file_extension: $ext,
            edit_context: {
                old_string_preview: $old_preview,
                new_string_preview: $new_preview
            },
            chain_id: (if $chain_id == "" then null else $chain_id end),
            chain_position: $chain_pos,
            chain_files: $chain_files,
            edit_sequence_id: $seq
        }' >> "$SESSION_FILE" 2>/dev/null
fi

exit 0
