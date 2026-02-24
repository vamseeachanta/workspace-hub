#!/usr/bin/env bash
# ABOUTME: Query AI agent usage/quota and display compact summary
# ABOUTME: Reads local data sources for Claude, Codex, and Gemini CLIs
set -euo pipefail

# Skip in subagent context — quota logging is a main-session concern only
[[ "${CLAUDE_SUBAGENT:-0}" == "1" ]] && exit 0

CACHE_FILE="${HOME}/.cache/agent-quota.json"
CACHE_TTL_SEC=900  # 15 minutes
USAGE_LOG_DIR="${HOME}/.agent-usage"
USAGE_LOG_FILE="${USAGE_LOG_DIR}/weekly-log.jsonl"

# Configurable limits — override in config/ai-tools/usage-tracking.yaml
# Claude stats-cache.json "messageCount" counts ALL conversation turns
# (user, assistant, tool_call, tool_result). Divide by MESSAGE_RATIO
# to approximate user-level requests for limit comparison.
CLAUDE_MESSAGE_RATIO=15  # ~15 raw msgs per user request on average

# Claude limits by subscription tier (user requests per week, approximate)
declare -A CLAUDE_WEEKLY_LIMITS=(
    [pro]=2000
    [max]=10000
    [default_claude_max_20x]=20000
    [team]=3500
)

# Codex: ~45-225 messages per 5h window for Plus, ~300-1500 for Pro (weekly)
CODEX_WEEKLY_MESSAGES=1400

# Gemini: 1000 requests/day for Google Login
GEMINI_DAILY_REQUESTS=1000

usage() {
    cat <<'EOF'
Usage:
  query-quota.sh              Show usage summary (uses cache)
  query-quota.sh --refresh    Force refresh (skip cache)
  query-quota.sh --json       Output JSON only
  query-quota.sh --log        Log current snapshot to weekly log
  query-quota.sh --weekly     Show weekly summary from log
EOF
}

# --- Portable OS helpers ---

# Portable file modification time (seconds since epoch)
file_mtime() {
    stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0
}

# Portable ISO-8601 datetime (YYYY-MM-DDTHH:MM:SS+TZ)
iso_now() {
    date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z
}

# Portable midnight timestamp for today (seconds since epoch)
today_midnight_ts() {
    local today
    today=$(date +%Y-%m-%d)
    # GNU date
    date -d "${today} 00:00:00" +%s 2>/dev/null && return
    # macOS/BSD date
    date -j -f "%Y-%m-%d %H:%M:%S" "${today} 00:00:00" +%s 2>/dev/null && return
    # Pure arithmetic fallback: current time minus seconds since midnight
    local h m s
    h=$(date +%H); m=$(date +%M); s=$(date +%S)
    echo $(( $(date +%s) - h*3600 - m*60 - s ))
}

# Portable last-Monday date string (YYYY-MM-DD)
last_monday_date() {
    # %u: 1=Mon ... 7=Sun (POSIX-ish, works on GNU and macOS)
    local dow days_back
    dow=$(date +%u 2>/dev/null || date +%w)  # %u preferred; %w=0 on Sun
    # Normalise: if %w gave us Sun=0, convert to 7
    [[ "$dow" == "0" ]] && dow=7
    days_back=$(( dow - 1 ))          # days since Monday (0 if today is Mon)
    (( days_back == 0 )) && days_back=7  # "last" Monday, not today
    # GNU date
    date -d "-${days_back} days" +%Y-%m-%d 2>/dev/null && return
    # macOS/BSD date
    date -v-${days_back}d +%Y-%m-%d 2>/dev/null && return
    # Fallback: 7-day window
    date -d "-7 days" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d
}

# Portable touch-to-midnight (for day-marker files)
touch_midnight() {
    local marker="$1" today="$2"
    touch -d "${today} 00:00:00" "$marker" 2>/dev/null && return
    # macOS: -t YYYYMMDDhhmm
    touch -t "$(echo "${today}" | tr -d '-')0000" "$marker" 2>/dev/null || true
}

# --- Data collection functions ---

query_claude() {
    local stats_file="${HOME}/.claude/stats-cache.json"
    local creds_file="${HOME}/.claude/.credentials.json"

    local tier="unknown"
    local weekly_limit=10000

    # Read subscription tier from credentials
    if [[ -f "$creds_file" ]]; then
        tier=$(jq -r '.claudeAiOauth.subscriptionType // "unknown"' "$creds_file" 2>/dev/null)
        local rate_tier
        rate_tier=$(jq -r '.claudeAiOauth.rateLimitTier // ""' "$creds_file" 2>/dev/null)
        if [[ -n "${CLAUDE_WEEKLY_LIMITS[$rate_tier]+x}" ]]; then
            weekly_limit=${CLAUDE_WEEKLY_LIMITS[$rate_tier]}
        elif [[ -n "${CLAUDE_WEEKLY_LIMITS[$tier]+x}" ]]; then
            weekly_limit=${CLAUDE_WEEKLY_LIMITS[$tier]}
        fi
    fi

    # Sum last-7-days usage from stats-cache.json using python3 for portable date math.
    # stats-cache.json dailyActivity[].date is a YYYY-MM-DD string; compare against
    # a cutoff date string derived from (now - 7*86400) to avoid GNU date dependency.
    local weekly_stats
    weekly_stats=$(python3 - <<PYEOF
import json, time, os, datetime
cache = os.path.expanduser("~/.claude/stats-cache.json")
try:
    with open(cache) as f:
        data = json.load(f)
    cutoff = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    messages = sessions = tools = 0
    for day in data.get("dailyActivity", []):
        if day.get("date", "") > cutoff:
            messages += day.get("messageCount", 0)
            sessions += day.get("sessionCount", 0)
            tools    += day.get("toolCallCount", 0)
    print(messages, sessions, tools)
except Exception:
    print(0, 0, 0)
PYEOF
)
    local messages sessions tools
    read -r messages sessions tools <<< "$weekly_stats"
    messages=${messages:-0}
    sessions=${sessions:-0}
    tools=${tools:-0}

    # Approximate user-level requests from raw message count
    local approx_requests
    approx_requests=$(awk -v m="$messages" -v r="$CLAUDE_MESSAGE_RATIO" \
        'BEGIN { printf "%d", m / r }')

    local pct_used=0
    if (( weekly_limit > 0 )); then
        pct_used=$(awk -v u="$approx_requests" -v l="$weekly_limit" \
            'BEGIN { printf "%d", (u/l)*100 }')
        (( pct_used > 100 )) && pct_used=100
    fi
    local pct_remaining=$(( 100 - pct_used ))

    # Compute 7-day average per day for trend comparison
    local avg_messages=0
    if [[ -f "$stats_file" ]]; then
        avg_messages=$(jq -r '[.dailyActivity[].messageCount] | add / length | floor' \
            "$stats_file" 2>/dev/null || echo 0)
    fi
    local trend="stable"
    # today's count for trend: last entry in dailyActivity (most recent date)
    local today_messages=0
    if [[ -f "$stats_file" ]]; then
        today_messages=$(jq -r '.dailyActivity[-1].messageCount // 0' \
            "$stats_file" 2>/dev/null || echo 0)
    fi
    if (( today_messages > 0 && avg_messages > 0 )); then
        local ratio
        ratio=$(awk -v t="$today_messages" -v a="$avg_messages" \
            'BEGIN { printf "%.1f", t / a }')
        if awk -v r="$ratio" 'BEGIN { exit !(r > 1.5) }'; then
            trend="high"
        elif awk -v r="$ratio" 'BEGIN { exit !(r < 0.5) }'; then
            trend="low"
        fi
    fi

    jq -n \
        --arg tier "$tier" \
        --argjson limit "$weekly_limit" \
        --argjson messages "$messages" \
        --argjson approx_requests "$approx_requests" \
        --argjson sessions "$sessions" \
        --argjson tools "$tools" \
        --argjson pct_remaining "$pct_remaining" \
        --argjson avg_messages "$avg_messages" \
        --arg trend "$trend" \
        '{
            provider: "claude",
            tier: $tier,
            weekly_limit: $limit,
            week_messages: $messages,
            approx_requests: $approx_requests,
            week_sessions: $sessions,
            week_tool_calls: $tools,
            pct_remaining: $pct_remaining,
            avg_daily_messages: $avg_messages,
            trend: $trend,
            source: "stats-cache.json"
        }'
}

query_codex() {
    local history_file="${HOME}/.codex/history.jsonl"

    # Count history.jsonl entries from the last 7 days using python3 for portable
    # epoch math — avoids GNU-only `date -d` and BSD `date -v` incompatibility.
    local messages=0
    if [[ -f "$history_file" ]]; then
        messages=$(python3 - <<PYEOF
import json, time, os
history = os.path.expanduser("~/.codex/history.jsonl")
cutoff = time.time() - 7 * 86400
count = 0
try:
    with open(history) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("ts", 0) >= cutoff:
                    count += 1
            except (json.JSONDecodeError, ValueError):
                pass
except Exception:
    pass
print(count)
PYEOF
)
        messages=${messages:-0}
    fi

    local pct_used=0
    if (( CODEX_WEEKLY_MESSAGES > 0 )); then
        pct_used=$(awk -v u="$messages" -v l="$CODEX_WEEKLY_MESSAGES" 'BEGIN { printf "%d", (u/l)*100 }')
        (( pct_used > 100 )) && pct_used=100
    fi
    local pct_remaining=$(( 100 - pct_used ))

    jq -n \
        --argjson limit "$CODEX_WEEKLY_MESSAGES" \
        --argjson messages "$messages" \
        --argjson pct_remaining "$pct_remaining" \
        '{
            provider: "codex",
            tier: "subscription",
            weekly_limit: $limit,
            week_messages: $messages,
            pct_remaining: $pct_remaining,
            source: "history.jsonl"
        }'
}

query_gemini() {
    local state_file="${HOME}/.config/gemini/state.json"
    local today messages=0
    today=$(date +%Y-%m-%d)

    if [[ -f "$state_file" ]]; then
        local count
        count=$(jq -r '.dailyRequestCount // 0' "$state_file" 2>/dev/null)
        [[ "$count" != "null" && "$count" != "0" ]] && messages=$count
    fi

    # Fallback: count session files created today
    if (( messages == 0 )); then
        [[ ! -f /tmp/.gemini-day-marker ]] && touch_midnight /tmp/.gemini-day-marker "$today"
        messages=$(find "${HOME}/.config/gemini/tmp" -maxdepth 1 \
            -newer /tmp/.gemini-day-marker -type f 2>/dev/null | wc -l)
    fi

    local pct_used=0
    if (( GEMINI_DAILY_REQUESTS > 0 )); then
        pct_used=$(awk -v u="$messages" -v l="$GEMINI_DAILY_REQUESTS" 'BEGIN { printf "%d", (u/l)*100 }')
        (( pct_used > 100 )) && pct_used=100
    fi

    jq -n \
        --argjson limit "$GEMINI_DAILY_REQUESTS" \
        --argjson messages "$messages" \
        --argjson pct_remaining "$(( 100 - pct_used ))" \
        '{ provider: "gemini", tier: "google_login", daily_limit: $limit,
           today_messages: $messages, pct_remaining: $pct_remaining, source: "estimated" }'
}

# --- Cache functions ---

is_cache_fresh() {
    [[ -f "$CACHE_FILE" ]] || return 1
    local cache_age
    cache_age=$(( $(date +%s) - $(file_mtime "$CACHE_FILE") ))
    (( cache_age < CACHE_TTL_SEC ))
}

write_cache() {
    local data="$1"
    mkdir -p "$(dirname "$CACHE_FILE")"
    echo "$data" > "$CACHE_FILE"
}

read_cache() {
    cat "$CACHE_FILE" 2>/dev/null
}

# --- Display functions ---

bar_graph() {
    local pct=$1
    local width=10
    local filled=$(( pct * width / 100 ))
    local empty=$(( width - filled ))
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="█"; done
    for ((i=0; i<empty; i++)); do bar+="░"; done
    echo "$bar"
}

color_for_pct() {
    local pct=$1
    if (( pct > 50 )); then
        echo "32"  # green
    elif (( pct > 20 )); then
        echo "33"  # yellow
    else
        echo "31"  # red
    fi
}

display_summary() {
    local data="$1"
    local today
    today=$(date +%Y-%m-%d)
    local dow
    dow=$(date +%A)

    echo ""
    echo "Agent Credits ($dow $today):"

    for provider in claude codex gemini; do
        local entry
        entry=$(echo "$data" | jq -r --arg p "$provider" '.agents[] | select(.provider == $p)')
        if [[ -z "$entry" ]]; then
            printf "  %-8s ░░░░░░░░░░  — (no data)\n" "$provider:"
            continue
        fi

        local pct
        pct=$(echo "$entry" | jq -r '.pct_remaining')
        local msgs
        msgs=$(echo "$entry" | jq -r '.week_messages // .today_messages // 0')
        local limit
        limit=$(echo "$entry" | jq -r '.weekly_limit // .daily_limit // 0')
        local bar
        bar=$(bar_graph "$pct")
        local color
        color=$(color_for_pct "$pct")

        local detail=""
        if [[ "$provider" == "claude" ]]; then
            local sessions tools approx trend
            sessions=$(echo "$entry" | jq -r '.week_sessions // .today_sessions // 0')
            tools=$(echo "$entry" | jq -r '.week_tool_calls // .today_tool_calls // 0')
            approx=$(echo "$entry" | jq -r '.approx_requests // 0')
            trend=$(echo "$entry" | jq -r '.trend // "stable"')
            local trend_icon=""
            case "$trend" in
                high) trend_icon=" ↑" ;;
                low)  trend_icon=" ↓" ;;
            esac
            detail="(~${approx} reqs, ${sessions} sessions, ${tools} tools${trend_icon})"
        else
            detail="(${msgs}/${limit} msgs)"
        fi

        printf "  %-8s \033[%sm%s\033[0m  %d%% remaining %s\n" \
            "$provider:" "$color" "$bar" "$pct" "$detail"
    done
    echo ""
}

# --- Logging functions ---

log_snapshot() {
    local data="$1"
    mkdir -p "$USAGE_LOG_DIR"

    local entry
    entry=$(jq -cn \
        --arg ts "$(iso_now)" \
        --argjson agents "$(echo "$data" | jq -c '.agents')" \
        '{ timestamp: $ts, agents: $agents }')

    echo "$entry" >> "$USAGE_LOG_FILE"
}

show_weekly_summary() {
    # Read directly from source files — does not require weekly-log.jsonl to be populated.
    local week_start
    week_start=$(last_monday_date)
    echo "Weekly Usage Summary (since $week_start):"
    echo ""

    # Claude: sum 7-day dailyActivity from stats-cache.json and report per-day breakdown
    local claude_stats
    claude_stats=$(python3 - <<PYEOF
import json, time, os, datetime
cache = os.path.expanduser("~/.claude/stats-cache.json")
try:
    with open(cache) as f:
        data = json.load(f)
    cutoff = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    total_msgs = peak = 0
    days_seen = 0
    for day in data.get("dailyActivity", []):
        if day.get("date", "") > cutoff:
            m = day.get("messageCount", 0)
            total_msgs += m
            days_seen += 1
            if m > peak:
                peak = m
    avg = total_msgs // days_seen if days_seen else 0
    print(total_msgs, peak, avg, days_seen)
except Exception:
    print(0, 0, 0, 0)
PYEOF
)
    local c_total c_peak c_avg c_days
    read -r c_total c_peak c_avg c_days <<< "$claude_stats"
    printf "  %-8s week msgs: %s  peak day: %s  avg/day: %s  (%s days)\n" \
        "claude:" "${c_total:-0}" "${c_peak:-0}" "${c_avg:-0}" "${c_days:-0}"

    # Codex: count history.jsonl entries from last 7 days
    local codex_count=0
    if [[ -f "${HOME}/.codex/history.jsonl" ]]; then
        codex_count=$(python3 - <<PYEOF
import json, time, os
history = os.path.expanduser("~/.codex/history.jsonl")
cutoff = time.time() - 7 * 86400
count = 0
try:
    with open(history) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("ts", 0) >= cutoff:
                    count += 1
            except (json.JSONDecodeError, ValueError):
                pass
except Exception:
    pass
print(count)
PYEOF
)
        codex_count=${codex_count:-0}
    fi
    printf "  %-8s week msgs: %s  (limit: %s)\n" \
        "codex:" "$codex_count" "$CODEX_WEEKLY_MESSAGES"

    # Gemini: weekly data not reliably available from source; show daily estimate
    local gemini_daily=0
    local gemini_state="${HOME}/.config/gemini/state.json"
    if [[ -f "$gemini_state" ]]; then
        gemini_daily=$(jq -r '.dailyRequestCount // 0' "$gemini_state" 2>/dev/null || echo 0)
    fi
    printf "  %-8s today msgs: %s  (weekly data not available from source)\n" \
        "gemini:" "$gemini_daily"
    echo ""
}

# --- Main ---

main() {
    local mode="display"
    local refresh=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --refresh) refresh=true; shift ;;
            --json)    mode="json"; shift ;;
            --log)     mode="log"; shift ;;
            --weekly)  mode="weekly"; shift ;;
            --help|-h) usage; exit 0 ;;
            *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
        esac
    done

    # Weekly summary doesn't need fresh data
    if [[ "$mode" == "weekly" ]]; then
        show_weekly_summary
        return
    fi

    # Check cache
    local data=""
    if [[ "$refresh" == "false" ]] && is_cache_fresh; then
        data=$(read_cache)
    fi

    # Collect fresh data if needed
    if [[ -z "$data" ]]; then
        local claude_data codex_data gemini_data
        claude_data=$(query_claude 2>/dev/null || echo '{"provider":"claude","pct_remaining":null}')
        codex_data=$(query_codex 2>/dev/null || echo '{"provider":"codex","pct_remaining":null}')
        gemini_data=$(query_gemini 2>/dev/null || echo '{"provider":"gemini","pct_remaining":null}')

        data=$(jq -n \
            --arg ts "$(date -Iseconds)" \
            --argjson claude "$claude_data" \
            --argjson codex "$codex_data" \
            --argjson gemini "$gemini_data" \
            '{
                timestamp: $ts,
                agents: [$claude, $codex, $gemini]
            }')

        write_cache "$data"
    fi

    case "$mode" in
        json)
            echo "$data" | jq '.'
            ;;
        log)
            log_snapshot "$data"
            echo "Logged usage snapshot to $USAGE_LOG_FILE"
            ;;
        display)
            display_summary "$data"
            ;;
    esac
}

main "$@"
