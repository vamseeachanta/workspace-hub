#!/usr/bin/env bash
# ABOUTME: Display and logging functions for AI usage reports
# Requires: utils.sh sourced, providers.sh sourced

bar_graph() {
    local pct=$1 width=10
    local filled=$(( pct * width / 100 ))
    local empty=$(( width - filled ))
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="█"; done
    for ((i=0; i<empty; i++)); do bar+="░"; done
    echo "$bar"
}

color_for_pct() {
    local pct=$1
    if (( pct > 50 )); then echo "32"
    elif (( pct > 20 )); then echo "33"
    else echo "31"; fi
}

display_summary() {
    local data="$1"
    echo ""
    echo "Agent Credits ($(date +%A) $(date +%Y-%m-%d)):"

    for provider in claude codex gemini; do
        local entry
        entry=$(echo "$data" | jq -r --arg p "$provider" '.agents[] | select(.provider == $p)')
        if [[ -z "$entry" ]]; then
            printf "  %-8s ░░░░░░░░░░  — (no data)\n" "$provider:"; continue
        fi

        local pct
        pct=$(echo "$entry" | jq -r '.pct_remaining // empty' 2>/dev/null || true)

        # No authoritative rate-limit % — keep Claude as N/A until fixed.
        if [[ -z "$pct" || "$pct" == "null" ]]; then
            printf "  %-8s ░░░░░░░░░░  N/A (authoritative source unavailable)\n" "$provider:"
            continue
        fi

        local msgs limit bar color detail
        msgs=$(echo "$entry" | jq -r '.week_messages // .today_messages // 0')
        limit=$(echo "$entry" | jq -r '.weekly_limit // .daily_limit // 0')
        bar=$(bar_graph "$pct")
        color=$(color_for_pct "$pct")

        if [[ "$provider" == "claude" ]]; then
            local approx sessions tools trend icon cost
            approx=$(echo "$entry" | jq -r '.approx_requests // 0')
            sessions=$(echo "$entry" | jq -r '.week_sessions // 0')
            tools=$(echo "$entry" | jq -r '.week_tool_calls // 0')
            trend=$(echo "$entry" | jq -r '.trend // "stable"')
            icon=""; case "$trend" in high) icon=" ↑" ;; low) icon=" ↓" ;; esac
            detail="(~${approx} reqs, ${sessions} sessions, ${tools} tools${icon})"
            cost=$(echo "$entry" | jq -r '.week_cost_usd // empty' 2>/dev/null || true)
            [[ -n "$cost" && "$cost" != "0" ]] && detail="\$${cost}/wk equiv, ${detail}"
        else
            detail="(${msgs}/${limit} msgs)"
        fi

        printf "  %-8s \033[%sm%s\033[0m  %d%% remaining %s\n" \
            "$provider:" "$color" "$bar" "$pct" "$detail"
    done
    echo ""
}

show_weekly_summary() {
    local week_start
    week_start=$(last_monday_date)
    echo "Weekly Usage Summary (since $week_start):"
    echo ""

    # Claude: authoritative OAuth snapshot only
    local oauth
    oauth=$(get_claude_oauth_entry)
    if [[ -n "$oauth" ]]; then
        local pct rem five reset
        pct=$(echo "$oauth" | jq -r '.week_pct // 0')
        rem=$(awk -v w="$pct" 'BEGIN { printf "%d", 100 - w }')
        five=$(echo "$oauth" | jq -r '.five_hour_pct // 0')
        reset=$(echo "$oauth" | jq -r '.hours_to_reset // 0')
        printf "  %-8s used: %s%%  remaining: %s%%  5h: %s%%  reset in: %sh\n" \
            "claude:" "$pct" "$rem" "$five" "$reset"
    else
        printf "  %-8s N/A  (authoritative source unavailable)\n" "claude:"
    fi

    # Codex: history.jsonl count
    local codex_count=0
    [[ -f "${HOME}/.codex/history.jsonl" ]] && \
        codex_count=$(uv run --no-project python -c "
import json, time, os
h=os.path.expanduser('~/.codex/history.jsonl'); cutoff=time.time()-7*86400; c=0
try:
    [c := c+1 for line in open(h) if line.strip() and json.loads(line).get('ts',0) >= cutoff]
except: pass
print(c)
" 2>/dev/null || echo 0)
    printf "  %-8s week msgs: %s  (limit: %s)\n" \
        "codex:" "$codex_count" "${CODEX_WEEKLY_MESSAGES:-1400}"

    # Gemini: daily count only (weekly not available)
    local gemini_count=0
    [[ -f "${HOME}/.config/gemini/state.json" ]] && \
        gemini_count=$(jq -r '.dailyRequestCount // 0' "${HOME}/.config/gemini/state.json" 2>/dev/null || echo 0)
    printf "  %-8s today msgs: %s  (weekly data unavailable from source)\n" \
        "gemini:" "$gemini_count"
    echo ""
}

log_snapshot() {
    local data="$1" log_file="$2"
    mkdir -p "$(dirname "$log_file")"
    jq -cn \
        --arg ts "$(iso_now)" \
        --argjson agents "$(echo "$data" | jq -c '.agents')" \
        '{ timestamp: $ts, agents: $agents }' >> "$log_file"
}
