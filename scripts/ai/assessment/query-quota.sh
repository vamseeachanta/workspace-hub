#!/usr/bin/env bash
# ABOUTME: AI agent usage/quota summary — Claude, Codex, Gemini
# ABOUTME: Sources lib/{utils,providers,display}.sh for modular implementation
# Usage: query-quota.sh [--refresh] [--json] [--log] [--weekly]

set -euo pipefail

# Skip in subagent context — quota logging is a main-session concern only
[[ "${CLAUDE_SUBAGENT:-0}" == "1" ]] && exit 0

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/lib"

source "$LIB_DIR/utils.sh"
source "$LIB_DIR/providers.sh"
source "$LIB_DIR/display.sh"

# ── Config ────────────────────────────────────────────────────────────────────
CACHE_FILE="${HOME}/.cache/agent-quota.json"
CACHE_TTL_SEC=900  # 15 minutes
USAGE_LOG_FILE="${HOME}/.agent-usage/weekly-log.jsonl"
REPO_QUOTA_FILE="${REPO_ROOT}/config/ai-tools/agent-quota-latest.json"
QUERY_REFRESH_MODE=false
CLAUDE_MESSAGE_RATIO=15   # raw turns per user request (approximate)
CODEX_WEEKLY_MESSAGES=1400
GEMINI_DAILY_REQUESTS=1000

# ── Cache helpers ─────────────────────────────────────────────────────────────
is_cache_fresh() {
    [[ -f "$CACHE_FILE" ]] || return 1
    local age=$(( $(date +%s) - $(file_mtime "$CACHE_FILE") ))
    (( age < CACHE_TTL_SEC ))
}

write_cache()      { mkdir -p "$(dirname "$CACHE_FILE")"; echo "$1" > "$CACHE_FILE"; }
read_cache()       { cat "$CACHE_FILE" 2>/dev/null; }
write_repo_quota() { mkdir -p "$(dirname "$REPO_QUOTA_FILE")"; echo "$1" | jq '.' > "$REPO_QUOTA_FILE"; }

# ── Usage ─────────────────────────────────────────────────────────────────────
usage() {
    cat <<'EOF'
Usage:
  query-quota.sh              Show usage summary (uses 15-min cache)
  query-quota.sh --refresh    Force refresh (skip cache)
  query-quota.sh --json       Output raw JSON
  query-quota.sh --log        Log snapshot to ~/.agent-usage/weekly-log.jsonl
  query-quota.sh --weekly     Show weekly summary (uses ccusage)
EOF
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    local mode="display" refresh=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --refresh) refresh=true;  shift ;;
            --json)    mode="json";   shift ;;
            --log)     mode="log";    shift ;;
            --weekly)  mode="weekly"; shift ;;
            --help|-h) usage; exit 0 ;;
            *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
        esac
    done

    QUERY_REFRESH_MODE="$refresh"

    if [[ "$mode" == "weekly" ]]; then
        show_weekly_summary; return
    fi

    local data=""
    [[ "$refresh" == "false" ]] && is_cache_fresh && data=$(read_cache)

    if [[ -z "$data" ]]; then
        local claude_data codex_data gemini_data
        claude_data=$(query_claude  2>/dev/null || echo '{"provider":"claude","pct_remaining":null}')
        codex_data=$(query_codex   2>/dev/null || echo '{"provider":"codex","pct_remaining":null}')
        gemini_data=$(query_gemini 2>/dev/null || echo '{"provider":"gemini","pct_remaining":null}')

        data=$(jq -n \
            --arg ts "$(date -Iseconds)" \
            --argjson claude  "$claude_data" \
            --argjson codex   "$codex_data" \
            --argjson gemini  "$gemini_data" \
            '{timestamp:$ts, agents:[$claude,$codex,$gemini]}')

        write_cache "$data"
        write_repo_quota "$data"
    fi

    case "$mode" in
        json)    echo "$data" | jq '.' ;;
        log)     log_snapshot "$data" "$USAGE_LOG_FILE"
                 echo "Logged to $USAGE_LOG_FILE" ;;
        display) display_summary "$data" ;;
    esac
}

main "$@"
