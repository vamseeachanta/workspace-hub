#!/usr/bin/env bash
# ABOUTME: Query Codex weekly usage and reset time (live app-server RPC first)
# ABOUTME: Falls back to token_count rate_limits parsing from ~/.codex/sessions

set -euo pipefail

SESSIONS_DIR="${HOME}/.codex/sessions"
MAX_FILES=20
MODE="text"
NO_LIVE="${CODEX_USAGE_NO_LIVE:-0}"

usage() {
    cat <<'EOF'
Usage:
  query-codex-usage.sh            Show weekly Codex usage summary
  query-codex-usage.sh --json     Output JSON only
  query-codex-usage.sh --no-live  Skip live app-server query (session logs only)

Env: CODEX_USAGE_NO_LIVE=1 (same as --no-live), CODEX_APPSERVER_WAIT (default 3s)
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) MODE="json"; shift ;;
        --no-live) NO_LIVE=1; shift ;;
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

# Live query via `codex app-server` JSON-RPC (account/rateLimits/read).
# Authoritative even when no Codex session ran recently — session-log parsing
# (below) freezes at the last session's view and goes stale across weekly
# window rollovers (observed 2026-06-04: logs said 21% used/resets Jun 7
# while live was 1% used/resets Jun 11).
# Protocol: JSONL over stdio; stdin must stay open until the response lands
# (immediate EOF kills the server before it answers), hence printf + sleep.
# The pipeline waits out the full sleep (~3s default) even after grep -m1
# matches — fine for the 4-hourly cron consumer.
get_live_rate_limits() {
    [[ "$NO_LIVE" == "1" ]] && return 1
    command -v codex >/dev/null 2>&1 || return 1
    command -v timeout >/dev/null 2>&1 || return 1

    # Integer-validate (review nit): bad values would only cost a stderr
    # line (the || true absorbs the arithmetic abort), but stay quiet.
    # Responses arrive in ~1s; 3s gives margin without dragging the cron.
    local wait_s="${CODEX_APPSERVER_WAIT:-3}" resp=""
    [[ "$wait_s" =~ ^[0-9]+$ ]] || wait_s=3
    resp=$({ printf '%s\n' \
        '{"method":"initialize","id":0,"params":{"clientInfo":{"name":"query-codex-usage","title":"Quota Query","version":"1.0.0"}}}' \
        '{"method":"initialized","params":{}}' \
        '{"method":"account/rateLimits/read","id":1}'
        sleep "$wait_s"
      } | timeout $(( wait_s + 9 )) codex app-server 2>/dev/null \
        | grep -m1 '"id":1') || true
    [[ -n "$resp" ]] || return 1

    # Map camelCase RPC fields onto the session-parser entry shape so main()
    # is source-agnostic. Reject payloads missing the weekly (secondary) lane.
    echo "$resp" | jq -ce '
        .result.rateLimits
        | select(.secondary.usedPercent != null and .secondary.resetsAt != null)
        | {
            week_pct: .secondary.usedPercent,
            resets_at_epoch: .secondary.resetsAt,
            five_hour_pct: (.primary.usedPercent // 0),
            five_hour_resets_at_epoch: (.primary.resetsAt // 0)
        }' 2>/dev/null || return 1
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
    local latest source_label="local-session-rate-limits"
    latest=$(get_live_rate_limits || true)
    if [[ -n "$latest" ]]; then
        source_label="app-server-live"
    else
        latest=$(get_latest_rate_limit_entry || true)
    fi

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
    source_file=$(echo "$latest" | jq -r '.session_file // "live:codex-app-server"')

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
        --arg source_label "$source_label" \
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
            source: $source_label,
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
