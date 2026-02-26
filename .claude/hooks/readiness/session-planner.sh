#!/usr/bin/env bash
# session-planner.sh — Predictive Session Planning (WRK-182)
# Outputs "Today's recommended plan" at session start.
# Reads pending WRK items + live quota snapshot; applies a complexity heuristic.
# Non-blocking: exits 0 always. Safe to remove when platform-native planning matures.
#
# Spec: specs/modules/predictive-session-planning.md
# Invoked by: hooks/readiness/readiness.sh (once per session)
# Target latency: <500ms (awk single-pass over frontmatter avoids per-field subshells)

set -uo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_HUB}/.claude/work-queue/pending"
QUOTA_FILE="${WORKSPACE_HUB}/config/ai-tools/agent-quota-latest.json"

# Heuristic constants (see spec for derivation)
# Complexity weight: effort units per task complexity level
WEIGHT_SIMPLE=1
WEIGHT_MEDIUM=3
WEIGHT_COMPLEX=8

# Priority multiplier: high-priority items ranked higher
PRIO_HIGH=3
PRIO_MEDIUM=2
PRIO_LOW=1

# Quota scale factor: remaining_pct * QUOTA_SCALE_FACTOR / 100 = effort_units available
QUOTA_SCALE_FACTOR=800

# Agent speed (relative, integer 10 = 1.0x baseline)
SPEED_CLAUDE=10
SPEED_CODEX=12
SPEED_GEMINI=9

# Max items to display in the plan
MAX_PLAN_ITEMS=5

# Minimum effort units available to bother planning (avoid empty output)
MIN_QUOTA_UNITS=10

# --- Graceful-exit helpers ---
plan_skip() {
    exit 0
}

# --- Quota reading ---
# Returns remaining percentage for a provider (integer 0-100)
# Falls back to 50 (neutral) if data unavailable
get_quota_remaining() {
    local provider="$1"
    local default=50
    [[ ! -f "$QUOTA_FILE" ]] && echo "$default" && return
    command -v jq &>/dev/null || { echo "$default"; return; }

    local week_pct sonnet_pct
    week_pct=$(jq -r --arg p "$provider" \
        '.agents[] | select(.provider==$p) | (.week_pct // 50)' \
        "$QUOTA_FILE" 2>/dev/null | head -1)
    sonnet_pct=$(jq -r --arg p "$provider" \
        '.agents[] | select(.provider==$p) | (.sonnet_pct // 0)' \
        "$QUOTA_FILE" 2>/dev/null | head -1)

    # Strip decimal for integer arithmetic
    week_pct="${week_pct%.*}"; week_pct="${week_pct:-50}"
    sonnet_pct="${sonnet_pct%.*}"; sonnet_pct="${sonnet_pct:-0}"

    local used remaining
    used=$(( sonnet_pct > week_pct ? sonnet_pct : week_pct ))
    remaining=$(( 100 - used ))
    [[ "$remaining" -lt 0 ]] && remaining=0
    echo "$remaining"
}

# --- Complexity to effort units ---
complexity_weight() {
    case "${1,,}" in
        simple|low|small)        echo "$WEIGHT_SIMPLE" ;;
        medium|moderate)         echo "$WEIGHT_MEDIUM" ;;
        complex|high|critical)   echo "$WEIGHT_COMPLEX" ;;
        *)                       echo "$WEIGHT_MEDIUM" ;;
    esac
}

# --- Priority to multiplier ---
priority_multiplier() {
    case "${1,,}" in
        high)    echo "$PRIO_HIGH" ;;
        medium)  echo "$PRIO_MEDIUM" ;;
        low)     echo "$PRIO_LOW" ;;
        *)       echo "$PRIO_MEDIUM" ;;
    esac
}

# --- Agent speed factor (integer, 10 = 1.0x) ---
provider_speed() {
    case "${1,,}" in
        claude)  echo "$SPEED_CLAUDE" ;;
        codex)   echo "$SPEED_CODEX" ;;
        gemini)  echo "$SPEED_GEMINI" ;;
        *)       echo "$SPEED_CLAUDE" ;;
    esac
}

# --- Minutes estimate from effort units and speed ---
# Base: 1 unit = 15 min at 1.0x speed → units * 150 / speed
effort_to_minutes() {
    echo $(( $1 * 150 / $2 ))
}

# --- Main planning logic ---
main() {
    [[ -d "$QUEUE_DIR" ]] || plan_skip

    local claude_remaining codex_remaining gemini_remaining
    claude_remaining=$(get_quota_remaining "claude")
    codex_remaining=$(get_quota_remaining "codex")
    gemini_remaining=$(get_quota_remaining "gemini")

    local quota_units
    quota_units=$(( claude_remaining * QUOTA_SCALE_FACTOR / 100 ))
    [[ "$quota_units" -lt "$MIN_QUOTA_UNITS" ]] && plan_skip

    # Single awk pass: parse all WRK frontmatter fields at once.
    # For each file, extract id, complexity, priority, provider, blocked_by,
    # and first # heading as title.
    # Output TSV: id|complexity|priority|provider|blocked_by|title
    local tsv
    tsv=$(awk '
        FNR==1 {
            # Flush previous file
            if (id != "" && blocked == "[]") {
                if (title == "") title = "(no title)"
                print id "|" complexity "|" priority "|" provider "|" blocked "|" title
            }
            # Reset per-file vars
            in_front=0; front_done=0; dash_count=0
            id=""; complexity="medium"; priority="medium"; provider="claude"
            blocked="[]"; title=""
        }
        /^---/ && !front_done {
            dash_count++
            if (dash_count == 1) { in_front=1; next }
            if (dash_count == 2) { in_front=0; front_done=1; next }
        }
        in_front {
            if (/^id:/)         { sub(/^id:[[:space:]]*/,""); gsub(/["\047[:space:]]/,""); id=$0 }
            if (/^complexity:/) { sub(/^complexity:[[:space:]]*/,""); gsub(/["\047[:space:]]/,""); complexity=$0 }
            if (/^priority:/)   { sub(/^priority:[[:space:]]*/,""); gsub(/["\047[:space:]]/,""); priority=$0 }
            if (/^provider:/)   { sub(/^provider:[[:space:]]*/,""); gsub(/["\047[:space:]]/,""); provider=$0 }
            if (/^blocked_by:/) { sub(/^blocked_by:[[:space:]]*/,""); gsub(/["\047[:space:]]/,""); blocked=$0 }
            next
        }
        # First markdown heading for title (outside frontmatter)
        /^# / && title == "" && front_done {
            sub(/^# /,"")
            title = substr($0, 1, 56)
            if (length($0) > 56) title = title "..."
        }
        END {
            if (id != "" && blocked == "[]") {
                if (title == "") title = "(no title)"
                print id "|" complexity "|" priority "|" provider "|" blocked "|" title
            }
        }
    ' "${QUEUE_DIR}"/WRK-*.md 2>/dev/null)

    [[ -z "$tsv" ]] && plan_skip

    # Score each item and collect candidates
    local candidates=()
    while IFS='|' read -r wrk_id complexity priority provider blocked title; do
        [[ -z "$wrk_id" ]] && continue
        [[ -z "$provider" ]] && provider="claude"

        local w p s effort minutes score
        w=$(complexity_weight "$complexity")
        p=$(priority_multiplier "$priority")
        s=$(provider_speed "$provider")
        effort=$w
        minutes=$(effort_to_minutes "$effort" "$s")
        score=$(( p * s * 100 / effort ))

        # Penalise items whose provider is quota-constrained (>80% used)
        local prov_remaining
        case "${provider,,}" in
            claude) prov_remaining="$claude_remaining" ;;
            codex)  prov_remaining="$codex_remaining" ;;
            gemini) prov_remaining="$gemini_remaining" ;;
            *)      prov_remaining="$claude_remaining" ;;
        esac
        [[ "$prov_remaining" -lt 20 ]] && score=$(( score / 2 ))

        candidates+=("${score}|${wrk_id}|${provider}|${complexity}|${priority}|${title}|${effort}|${minutes}")
    done <<< "$tsv"

    [[ "${#candidates[@]}" -eq 0 ]] && plan_skip

    # Sort by score descending, take top N
    local sorted
    sorted=$(printf '%s\n' "${candidates[@]}" | sort -t'|' -k1 -rn | head -"$MAX_PLAN_ITEMS")

    # Accumulate totals for the selected items
    local total_effort=0 total_minutes=0
    while IFS='|' read -r score wrk_id provider complexity priority title effort minutes; do
        total_effort=$(( total_effort + effort ))
        total_minutes=$(( total_minutes + minutes ))
    done <<< "$sorted"

    # Completion probability
    local completion_pct=100
    if [[ "$total_effort" -gt 0 ]]; then
        completion_pct=$(( quota_units * 100 / total_effort ))
        [[ "$completion_pct" -gt 100 ]] && completion_pct=100
    fi

    # Output the plan
    echo "Session Plan (claude ${claude_remaining}% quota remaining):"

    local rank=0
    while IFS='|' read -r score wrk_id provider complexity priority title effort minutes; do
        rank=$(( rank + 1 ))
        local time_str
        if [[ "$minutes" -ge 60 ]]; then
            time_str="~$(( minutes / 60 ))h$(( minutes % 60 ))m"
        else
            time_str="~${minutes}m"
        fi
        printf '  %d. %-10s [%-7s/%-6s] %-7s — %s\n' \
            "$rank" "$wrk_id" "$complexity" "${provider:0:6}" "$time_str" "$title"
    done <<< "$sorted"

    local total_str
    if [[ "$total_minutes" -ge 60 ]]; then
        total_str="~$(( total_minutes / 60 ))h$(( total_minutes % 60 ))m"
    else
        total_str="~${total_minutes}m"
    fi

    echo "  Total estimated: ${total_str} | Completion probability: ${completion_pct}%"
}

main
exit 0
