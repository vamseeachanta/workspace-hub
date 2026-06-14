#!/usr/bin/env bash
# ABOUTME: AI provider usage query functions (Claude, Codex, Gemini)
# Requires: utils.sh sourced, REPO_QUOTA_FILE/CLAUDE_MESSAGE_RATIO globals set

# ── Claude ────────────────────────────────────────────────────────────────────

# Returns current-week cost/token data from ccusage (reads session JSONL — always current)
# Note: auxiliary only; not authoritative for quota percentages.
get_ccusage_weekly() {
    command -v npx &>/dev/null || { echo "null"; return; }
    local since raw
    since=$(this_monday_yyyymmdd 2>/dev/null || date -d "-7 days" +%Y%m%d)
    raw=$(NO_COLOR=1 npx ccusage weekly --json --since "$since" 2>/dev/null)
    [[ -z "$raw" ]] && { echo "null"; return; }
    echo "$raw" | uv run --no-project python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    weeks = data.get('weekly', [])
    if not weeks:
        print('null'); sys.exit(0)
    w = weeks[-1]
    print(json.dumps({
        'cost_usd':     round(w.get('totalCost', 0), 2),
        'total_tokens': w.get('totalTokens', 0),
        'input_tokens': w.get('inputTokens', 0),
        'output_tokens': w.get('outputTokens', 0),
        'models':       w.get('modelsUsed', [])
    }))
except Exception:
    print('null')
" 2>/dev/null || echo "null"
}

# Returns validated claude entry from REPO_QUOTA_FILE (authoritative only)
get_claude_oauth_entry() {
    [[ -f "$REPO_QUOTA_FILE" ]] || return 0
    local entry
    entry=$(jq -c '.agents[] | select(.provider == "claude") | select(.source == "oauth-api")' \
        "$REPO_QUOTA_FILE" 2>/dev/null || true)
    [[ -z "$entry" ]] && return 0
    echo "$entry" | jq -e '.week_pct != null' &>/dev/null && echo "$entry"
}

# Returns weekly stats from ~/.claude/stats-cache.json (local CLI tracker, may be stale)
query_claude_stats() {
    local creds="${HOME}/.claude/.credentials.json"
    local stats="${HOME}/.claude/stats-cache.json"
    local tier="unknown" weekly_limit=10000

    if [[ -f "$creds" ]]; then
        tier=$(jq -r '.claudeAiOauth.subscriptionType // "unknown"' "$creds" 2>/dev/null)
        local rate_tier
        rate_tier=$(jq -r '.claudeAiOauth.rateLimitTier // ""' "$creds" 2>/dev/null)
        case "${rate_tier:-$tier}" in
            pro)                   weekly_limit=2000  ;;
            max)                   weekly_limit=10000 ;;
            default_claude_max_20x) weekly_limit=20000 ;;
            team)                  weekly_limit=3500  ;;
        esac
    fi

    local weekly
    weekly=$(uv run --no-project python - <<PYEOF
import json, datetime, os
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
    read -r messages sessions tools <<< "$weekly"
    messages=${messages:-0}; sessions=${sessions:-0}; tools=${tools:-0}

    local approx=0 pct_used=0 pct_remaining=100
    if (( weekly_limit > 0 && messages > 0 )); then
        approx=$(awk -v m="$messages" -v r="${CLAUDE_MESSAGE_RATIO:-15}" 'BEGIN { printf "%d", m/r }')
        pct_used=$(awk -v u="$approx" -v l="$weekly_limit" 'BEGIN { printf "%d", (u/l)*100 }')
        (( pct_used > 100 )) && pct_used=100
        pct_remaining=$(( 100 - pct_used ))
    fi

    local avg=0 trend="stable"
    if [[ -f "$stats" ]]; then
        avg=$(jq -r '[.dailyActivity[].messageCount] | add / length | floor' "$stats" 2>/dev/null || echo 0)
        local today_msgs
        today_msgs=$(jq -r '.dailyActivity[-1].messageCount // 0' "$stats" 2>/dev/null || echo 0)
        if (( today_msgs > 0 && avg > 0 )); then
            awk -v t="$today_msgs" -v a="$avg" 'BEGIN { exit !(t/a > 1.5) }' && trend="high"
            awk -v t="$today_msgs" -v a="$avg" 'BEGIN { exit !(t/a < 0.5) }' && trend="low"
        fi
    fi

    jq -n \
        --arg tier "$tier" \
        --argjson limit "$weekly_limit" \
        --argjson messages "$messages" \
        --argjson approx "$approx" \
        --argjson sessions "$sessions" \
        --argjson tools "$tools" \
        --argjson pct "$pct_remaining" \
        --argjson avg "$avg" \
        --arg trend "$trend" \
        '{provider:"claude", tier:$tier, weekly_limit:$limit,
          week_messages:$messages, approx_requests:$approx,
          week_sessions:$sessions, week_tool_calls:$tools,
          pct_remaining:$pct, avg_daily_messages:$avg,
          trend:$trend, source:"stats-cache.json"}'
}

# Merges ccusage token/cost data into a provider JSON entry as auxiliary metadata only.
# Use this only when the base quota source is authoritative.
_enrich_with_ccusage() {
    local entry="$1"
    local ccusage
    ccusage=$(get_ccusage_weekly)
    [[ "$ccusage" == "null" || -z "$ccusage" ]] && { echo "$entry"; return; }
    echo "$entry" | jq \
        --argjson cc "$ccusage" \
        '. + {week_cost_usd: $cc.cost_usd, week_tokens: $cc.total_tokens,
              week_input_tokens: $cc.input_tokens, week_output_tokens: $cc.output_tokens,
              models_used: $cc.models}'
}

# Main claude query: authoritative OAuth snapshot only.
# If unavailable, surface N/A rather than an estimated quota.
query_claude() {
    local oauth
    oauth=$(get_claude_oauth_entry)
    if [[ -n "$oauth" ]]; then
        _enrich_with_ccusage "$oauth"
        return
    fi

    local creds="${HOME}/.claude/.credentials.json"
    local tier="unknown" weekly_limit=10000
    if [[ -f "$creds" ]]; then
        tier=$(jq -r '.claudeAiOauth.subscriptionType // "unknown"' "$creds" 2>/dev/null)
        local rate_tier
        rate_tier=$(jq -r '.claudeAiOauth.rateLimitTier // ""' "$creds" 2>/dev/null)
        case "${rate_tier:-$tier}" in
            pro)                    weekly_limit=2000  ;;
            max)                    weekly_limit=10000 ;;
            default_claude_max_20x) weekly_limit=20000 ;;
            team)                   weekly_limit=3500  ;;
        esac
    fi

    local unavailable
    jq -n \
        --arg tier "$tier" \
        --argjson limit "$weekly_limit" \
        '{
            provider:"claude",
            tier:$tier,
            weekly_limit:$limit,
            week_pct:null,
            five_hour_pct:null,
            pct_remaining:null,
            hours_to_reset:null,
            resets_at:"",
            source:"unavailable"
        }'
}

# ── Codex ─────────────────────────────────────────────────────────────────────

query_codex() {
    local history="${HOME}/.codex/history.jsonl"
    local messages=0
    if [[ -f "$history" ]]; then
        messages=$(uv run --no-project python - <<PYEOF
import json, time, os
history = os.path.expanduser("~/.codex/history.jsonl")
cutoff = time.time() - 7 * 86400
count = 0
try:
    with open(history) as f:
        for line in f:
            line = line.strip()
            if not line: continue
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
    local limit="${CODEX_WEEKLY_MESSAGES:-1400}"

    # Authoritative: Codex's own server-reported rate-limit telemetry
    # (rate_limits.secondary in each session rollout). This matches the
    # ChatGPT Codex Analytics dashboard exactly. The history.jsonl
    # message-count below is a coarse estimate that wildly undercounts
    # (assumes a flat 1400-msg cap, ignores token/tool weighting) and is
    # used only as a fallback when no session telemetry is available.
    local assess_dir telemetry
    assess_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
    telemetry=$(bash "$assess_dir/query-codex-usage.sh" --json 2>/dev/null || true)
    # Accept either live app-server telemetry (preferred — survives weekly
    # window rollovers with no recent local session) or session-log telemetry.
    if [[ -n "$telemetry" ]] \
        && echo "$telemetry" | jq -e '(.source == "app-server-live" or .source == "local-session-rate-limits") and .pct_remaining != null' &>/dev/null; then
        echo "$telemetry" | jq -c \
            --argjson limit "$limit" \
            --argjson messages "$messages" \
            '{provider:"codex", tier:"subscription", weekly_limit:$limit,
              week_messages:$messages, week_pct:.week_pct,
              five_hour_pct:.five_hour_pct, pct_remaining:.pct_remaining,
              hours_to_reset:.hours_to_reset, resets_at:.resets_at,
              source:.source}'
        return
    fi

    # Fallback: coarse message-count estimate (no live rate-limit telemetry).
    local pct_used=0
    (( limit > 0 )) && pct_used=$(awk -v u="$messages" -v l="$limit" 'BEGIN { printf "%d", (u/l)*100 }')
    (( pct_used > 100 )) && pct_used=100
    jq -n \
        --argjson limit "$limit" \
        --argjson messages "$messages" \
        --argjson pct "$(( 100 - pct_used ))" \
        '{provider:"codex", tier:"subscription", weekly_limit:$limit,
          week_messages:$messages, pct_remaining:$pct, source:"history.jsonl-estimate"}'
}

# ── Gemini ────────────────────────────────────────────────────────────────────

# Genuine Gemini (agy) usage via the shared source of truth, scripts/ai/assessment/
# gemini-usage.py (429-throttle → manual /usage snapshot → unavailable). agy
# persists no quota to disk (workspace-hub#3087), so the legacy file-count
# "estimated" %/daily_limit:1000 was fabricated — replaced here. Surfaces
# pct_remaining:null / source:"unavailable" when no genuine signal exists, matching
# the Claude convention above ("surface N/A rather than an estimated quota").
query_gemini() {
    local helper g
    helper="$(dirname "${BASH_SOURCE[0]}")/../gemini-usage.py"
    g=$(python3 "$helper" 2>/dev/null) || g=""
    [[ -n "$g" ]] || g='{"pct_remaining":null,"five_hour_pct":null,"hours_to_reset":null,"resets_at":null,"captured_at":null,"source":"unavailable"}'
    echo "$g" | jq '{
        provider: "gemini",
        tier: "google_login",
        week_pct: (if .pct_remaining == null then null else (100 - .pct_remaining) end),
        five_hour_pct: .five_hour_pct,
        pct_remaining: .pct_remaining,
        hours_to_reset: .hours_to_reset,
        resets_at: (.resets_at // ""),
        captured_at: .captured_at,
        source: .source
    }'
}
