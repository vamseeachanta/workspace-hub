#!/usr/bin/env bash
# ABOUTME: Query Codex weekly usage and reset time from local Codex session logs
# ABOUTME: Parses latest token_count rate_limits.secondary values from ~/.codex/sessions

set -euo pipefail

SESSIONS_DIR="${HOME}/.codex/sessions"
MAX_FILES=20
MODE="text"

usage() {
    cat <<'EOF'
Usage:
  query-codex-usage.sh         Show weekly Codex usage summary
  query-codex-usage.sh --json  Output JSON only
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) MODE="json"; shift ;;
        --help|-h) usage; exit 0 ;;
        *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
    esac
done

to_local_iso() {
    local epoch="$1"
    date -d "@$epoch" +"%Y-%m-%dT%H:%M:%S%z" 2>/dev/null || echo ""
}

to_local_human() {
    local epoch="$1"
    date -d "@$epoch" +"%Y-%m-%d %H:%M:%S %Z" 2>/dev/null || echo "unknown"
}

format_time_left() {
    local total_seconds="$1"
    if (( total_seconds <= 0 )); then
        echo "0h"
        return
    fi

    local days hours minutes
    days=$(( total_seconds / 86400 ))
    hours=$(( (total_seconds % 86400) / 3600 ))
    minutes=$(( (total_seconds % 3600) / 60 ))

    if (( days > 0 )); then
        echo "${days}d${hours}h"
    elif (( hours > 0 )); then
        echo "${hours}h${minutes}m"
    else
        echo "${minutes}m"
    fi
}

get_latest_rate_limit_entry() {
    [[ -d "$SESSIONS_DIR" ]] || return 1

    local candidates
    candidates=$(find "$SESSIONS_DIR" -type f -name '*.jsonl' -printf '%T@ %p\n' 2>/dev/null \
        | sort -nr \
        | head -n "$MAX_FILES" \
        | awk '{print $2}')

    [[ -n "$candidates" ]] || return 1

    local file entry
    for file in $candidates; do
        entry=$(tail -n 1200 "$file" 2>/dev/null | jq -rc '
            select(
                .type == "event_msg"
                and .payload.type == "token_count"
                and (.payload.rate_limits.secondary.used_percent != null)
                and (.payload.rate_limits.secondary.resets_at != null)
            )
            | {
                timestamp: .timestamp,
                week_pct: .payload.rate_limits.secondary.used_percent,
                resets_at_epoch: .payload.rate_limits.secondary.resets_at,
                five_hour_pct: .payload.rate_limits.primary.used_percent,
                five_hour_resets_at_epoch: .payload.rate_limits.primary.resets_at
            }
        ' 2>/dev/null | tail -n 1 || true)

        if [[ -n "$entry" ]]; then
            jq -cn --arg file "$file" --argjson data "$entry" '$data + {session_file: $file}'
            return 0
        fi
    done

    return 1
}

manual_fallback() {
    local manual_file="${HOME}/.cache/agent-quota-manual.json"
    local week_pct=0 resets_at=""
    if [[ -f "$manual_file" ]]; then
        week_pct=$(jq -r '.codex // 0' "$manual_file" 2>/dev/null || echo 0)
        resets_at=$(jq -r '.codex_resets_at // ""' "$manual_file" 2>/dev/null || echo "")
    fi

    jq -cn \
        --argjson week_pct "${week_pct:-0}" \
        --arg resets_at "$resets_at" \
        '{
            provider: "codex",
            week_pct: $week_pct,
            pct_remaining: (100 - ($week_pct | floor)),
            resets_at: $resets_at,
            hours_to_reset: null,
            source: "manual"
        }'
}

main() {
    local latest
    latest=$(get_latest_rate_limit_entry || true)

    if [[ -z "$latest" ]]; then
        local fallback
        fallback=$(manual_fallback)
        if [[ "$MODE" == "json" ]]; then
            echo "$fallback" | jq '.'
        else
            local week_pct remaining
            week_pct=$(echo "$fallback" | jq -r '.week_pct')
            remaining=$(echo "$fallback" | jq -r '.pct_remaining')
            echo "Codex Weekly Usage"
            echo "  Used: ${week_pct}%"
            echo "  Remaining: ${remaining}%"
            echo "  Source: manual (set via query-quota.sh --set codex=<pct> codex_resets_at=<ISO>)"
        fi
        return 0
    fi

    local week_pct resets_at_epoch five_hour_pct five_hour_resets_at_epoch source_file
    week_pct=$(echo "$latest" | jq -r '.week_pct')
    resets_at_epoch=$(echo "$latest" | jq -r '.resets_at_epoch')
    five_hour_pct=$(echo "$latest" | jq -r '.five_hour_pct // 0')
    five_hour_resets_at_epoch=$(echo "$latest" | jq -r '.five_hour_resets_at_epoch // 0')
    source_file=$(echo "$latest" | jq -r '.session_file')

    local now_epoch pct_remaining seconds_to_reset hours_to_reset
    now_epoch=$(date +%s)
    pct_remaining=$(awk "BEGIN { v = 100 - $week_pct; if (v < 0) v = 0; printf \"%.0f\", v }")
    seconds_to_reset=$(( resets_at_epoch - now_epoch ))
    if (( seconds_to_reset < 0 )); then
        seconds_to_reset=0
    fi
    hours_to_reset=$(( seconds_to_reset / 3600 ))

    local resets_at_local_iso resets_at_local_human
    resets_at_local_iso=$(to_local_iso "$resets_at_epoch")
    resets_at_local_human=$(to_local_human "$resets_at_epoch")

    local output
    output=$(jq -cn \
        --argjson week_pct "$week_pct" \
        --argjson pct_remaining "$pct_remaining" \
        --arg resets_at "$resets_at_local_iso" \
        --argjson resets_at_epoch "$resets_at_epoch" \
        --argjson hours_to_reset "$hours_to_reset" \
        --argjson five_hour_pct "$five_hour_pct" \
        --argjson five_hour_resets_at_epoch "$five_hour_resets_at_epoch" \
        --arg session_file "$source_file" \
        --arg updated_at "$(date -Iseconds)" \
        '{
            provider: "codex",
            week_pct: $week_pct,
            pct_remaining: $pct_remaining,
            resets_at: $resets_at,
            resets_at_epoch: $resets_at_epoch,
            hours_to_reset: $hours_to_reset,
            five_hour_pct: $five_hour_pct,
            five_hour_resets_at_epoch: $five_hour_resets_at_epoch,
            source: "local-session-rate-limits",
            session_file: $session_file,
            updated_at: $updated_at
        }')

    if [[ "$MODE" == "json" ]]; then
        echo "$output" | jq '.'
        return 0
    fi

    echo "Codex Weekly Usage"
    echo "  Used: ${week_pct}%"
    echo "  Remaining: ${pct_remaining}%"
    echo "  Expires: ${resets_at_local_human} ($(format_time_left "$seconds_to_reset"))"
    echo "  5h Window Used: ${five_hour_pct}%"
    echo "  Source: ${source_file}"
}

main "$@"
