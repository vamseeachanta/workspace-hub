#!/usr/bin/env bash
# extract-script-ideas.sh - Identify script opportunities from session patterns
# Part of RAGS loop: Detects repeated command patterns that could become scripts
#
# Input: Session logs from session-logger.sh
# Output: JSON with script ideas, enhancement suggestions, and skill candidates
# Platform: Linux, macOS, Windows (Git Bash/WSL)

set -uo pipefail

# Detect workspace hub (cross-platform)
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(detect_workspace_hub)"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}"
SESSIONS_DIR="${STATE_DIR}/sessions"
SKILLS_DIR="${WORKSPACE_HUB}/.claude/skills"
OUTPUT_DIR="${STATE_DIR}/script-ideas"
DAYS=${1:-7}
JQ_FILTER="${SCRIPT_DIR}/extract-script-ideas.jq"

mkdir -p "$OUTPUT_DIR"

# Find session files from last N days
SESSION_FILES=$(find "$SESSIONS_DIR" -name "session_*.jsonl" -mtime -"$DAYS" 2>/dev/null | sort)

if [[ -z "$SESSION_FILES" ]]; then
    echo '{"sessions_analyzed": 0, "script_ideas": [], "enhancement_suggestions": [], "skill_candidates": []}'
    exit 0
fi

# Combine all sessions into a temp file
TEMP_FILE=$(mktemp)
for f in $SESSION_FILES; do
    cat "$f" >> "$TEMP_FILE"
done

if [[ ! -s "$TEMP_FILE" ]]; then
    rm -f "$TEMP_FILE"
    echo '{"sessions_analyzed": 0, "script_ideas": [], "enhancement_suggestions": [], "skill_candidates": []}'
    exit 0
fi

# Get existing scripts for enhancement detection
EXISTING_SCRIPTS=$(find "$WORKSPACE_HUB" -name "*.sh" -type f 2>/dev/null | xargs -I{} basename {} .sh 2>/dev/null | sort -u | jq -R . | jq -s . 2>/dev/null || echo '[]')

# Check if jq filter file exists
if [[ ! -f "$JQ_FILTER" ]]; then
    echo '{"error": "jq filter file not found", "sessions_analyzed": 0}'
    rm -f "$TEMP_FILE"
    exit 1
fi

# Analyze with jq using external filter file
jq -s -f "$JQ_FILTER" \
    --argjson existing "$EXISTING_SCRIPTS" \
    --arg days "$DAYS" \
    "$TEMP_FILE" 2>/dev/null || echo '{"error": "jq processing failed", "sessions_analyzed": 0}'

# Cleanup
rm -f "$TEMP_FILE"
