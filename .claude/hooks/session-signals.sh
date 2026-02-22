#!/usr/bin/env bash
# session-signals.sh — lightweight session-end signal capture (<2s)
# Writes raw signals to state/session-signals/ for morning cron analysis
# NO analysis, NO scoring, NO WRK item creation here
#
# Trigger: Stop event (session end)
# Output: .claude/state/session-signals/YYYY-MM-DD-HHMMSS.jsonl
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq (optional), git, date

set -uo pipefail

# --- Workspace resolution ---
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate
    candidate="$(cd "$script_dir/../.." && pwd)"
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
SIGNALS_DIR="${WS_HUB}/.claude/state/session-signals"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATETIME_TAG=$(date +"%Y-%m-%d-%H%M%S")
OUTPUT_FILE="${SIGNALS_DIR}/${DATETIME_TAG}.jsonl"

# Ensure output directory exists
mkdir -p "$SIGNALS_DIR" 2>/dev/null || {
    echo "session-signals: ERROR: cannot create ${SIGNALS_DIR}" >&2
    exit 1
}

# --- Raw signal capture (fast, no heavy analysis) ---

# WRK items touched: scan recent git log for WRK-NNN references
wrk_items_touched="[]"
if command -v git &>/dev/null && git -C "$WS_HUB" rev-parse --git-dir &>/dev/null; then
    # Look at commits from the past 24 hours
    raw_wrk=$(git -C "$WS_HUB" log --oneline --since="24 hours ago" 2>/dev/null \
        | grep -oE 'WRK-[0-9]+' | sort -u | head -20 || true)
    if [[ -n "$raw_wrk" ]]; then
        # Build JSON array from newline-separated WRK IDs
        wrk_items_touched=$(printf '%s\n' "$raw_wrk" \
            | awk 'BEGIN{printf "["} NR>1{printf ","} {printf "\"%s\"",$0} END{printf "]"}')
    fi
fi

# Uncommitted changes: true/false
uncommitted_changes="false"
if command -v git &>/dev/null && git -C "$WS_HUB" rev-parse --git-dir &>/dev/null; then
    if ! git -C "$WS_HUB" diff --quiet 2>/dev/null || ! git -C "$WS_HUB" diff --cached --quiet 2>/dev/null; then
        uncommitted_changes="true"
    fi
fi

# Session duration from env (Claude Code may set CLAUDE_SESSION_START_TIME or similar)
session_duration_s="null"
if [[ -n "${CLAUDE_SESSION_START_TIME:-}" ]]; then
    start_epoch="$CLAUDE_SESSION_START_TIME"
    now_epoch=$(date +%s)
    session_duration_s=$(( now_epoch - start_epoch ))
fi

# Skill invocations: check hook input for skill names (Claude Code passes hook data via stdin)
HOOK_INPUT=""
if [[ ! -t 0 ]]; then
    HOOK_INPUT=$(cat 2>/dev/null || true)
fi

# Extract skill names from hook input if it's JSON
skill_invocations="[]"
if [[ -n "$HOOK_INPUT" ]] && command -v jq &>/dev/null; then
    raw_skills=$(printf '%s' "$HOOK_INPUT" \
        | jq -r '.. | objects | select(has("skill")) | .skill' 2>/dev/null \
        | sort -u | head -20 || true)
    if [[ -n "$raw_skills" ]]; then
        skill_invocations=$(printf '%s\n' "$raw_skills" \
            | awk 'BEGIN{printf "["} NR>1{printf ","} {printf "\"%s\"",$0} END{printf "]"}')
    fi
fi

# --- Write signal file ---
# One JSONL line per session end, using printf for reliable output
printf '%s\n' "$(cat <<SIGNAL_EOF
{"ts":"${TIMESTAMP}","event":"session_end","signals":{"skill_invocations":${skill_invocations},"tool_calls":[],"script_calls":[],"correction_events":[],"new_files":[],"wrk_items_touched":${wrk_items_touched},"uncommitted_changes":${uncommitted_changes},"session_duration_s":${session_duration_s}}}
SIGNAL_EOF
)" >> "$OUTPUT_FILE" 2>/dev/null || {
    echo "session-signals: ERROR: cannot write to ${OUTPUT_FILE}" >&2
    exit 1
}

echo "session-signals: wrote ${OUTPUT_FILE} (wrk=${wrk_items_touched} uncommitted=${uncommitted_changes})"
exit 0
