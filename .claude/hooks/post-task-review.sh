#!/usr/bin/env bash
# post-task-review.sh — Post-task learning check
# Trigger: Stop hook (end of session)
# Purpose: Summarize insights found and prompt skill/memory rollup
#
# Uses insights from session-review.sh output and prompts the agent
# to verify learnings are captured in skills and memory.
#
# Portable: resolves workspace-hub from script location or env var.
# Other repos should symlink or reference via ${WORKSPACE_HUB}.
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq

set -uo pipefail

# --- Workspace resolution (same pattern as session-review.sh) ---
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate="$(cd "$script_dir/../.." && pwd)"
    if [[ -d "$candidate/.claude" ]]; then
        echo "$candidate"
        return
    fi
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            for dir in "/d/workspace-hub" "/c/workspace-hub" "/c/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
        *)
            for dir in "$HOME/workspace-hub" "$HOME/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
    esac
    echo "$HOME/.claude"
}

WS_HUB="$(detect_workspace_hub)"
REVIEW_DIR="${WS_HUB}/.claude/state/pending-reviews"
PROJECT_NAME="$(basename "$(pwd)")"

# Consume stdin (hook may pipe data)
if [[ ! -t 0 ]]; then
    cat > /dev/null 2>&1 || true
fi

# --- Collect insights from today's session-review output ---
insights_summary=""
INSIGHTS_FILE="${REVIEW_DIR}/insights.jsonl"
SKILLS_FILE="${REVIEW_DIR}/skill-candidates.jsonl"
MEMORY_FILE="${REVIEW_DIR}/memory-updates.jsonl"

insights_count=0
skills_count=0
memory_count=0

if [[ -f "$INSIGHTS_FILE" ]]; then
    insights_count=$(wc -l < "$INSIGHTS_FILE" 2>/dev/null | tr -d ' ')
fi
if [[ -f "$SKILLS_FILE" ]]; then
    skills_count=$(wc -l < "$SKILLS_FILE" 2>/dev/null | tr -d ' ')
fi
if [[ -f "$MEMORY_FILE" ]]; then
    memory_count=$(wc -l < "$MEMORY_FILE" 2>/dev/null | tr -d ' ')
fi

# --- Output the learning check prompt ---
echo ""
echo "================================================================"
echo "  POST-TASK LEARNING CHECK — ${PROJECT_NAME}"
echo "================================================================"
echo ""

if [[ "$insights_count" -gt 0 ]]; then
    echo "  Insights detected: ${insights_count}"
    # Show last 3 insight previews
    tail -3 "$INSIGHTS_FILE" 2>/dev/null | jq -r '.content_preview // "" | .[0:120]' 2>/dev/null | while IFS= read -r line; do
        [[ -n "$line" ]] && echo "    - ${line}"
    done
fi
if [[ "$skills_count" -gt 0 ]]; then
    echo "  Skill candidates: ${skills_count} (repeated tool patterns)"
fi
if [[ "$memory_count" -gt 0 ]]; then
    echo "  Memory updates: ${memory_count}"
fi

echo ""
echo "  CHECKLIST:"
echo "    [ ] Are all learnings rolled into appropriate skills?"
echo "    [ ] Are gotchas/conventions saved to memory topic files?"
echo "    [ ] Are new patterns documented (not just in code comments)?"
echo "    [ ] Do existing skills need updates from this session?"
echo ""
echo "  Skill locations:  .claude/skills/<domain>/SKILL.md"
echo "  Memory location:  ~/.claude/projects/<key>/memory/"
echo "  Insights log:     ${INSIGHTS_FILE##*/}"
echo "================================================================"

exit 0
