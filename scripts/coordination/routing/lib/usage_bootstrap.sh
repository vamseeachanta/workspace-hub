#!/usr/bin/env bash
#
# Usage Bootstrap - creates zero-state usage tracking files
#

bootstrap_usage_files() {
    local config_dir="${CONFIG_DIR:?CONFIG_DIR must be set}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local -A budgets=(
        [claude]=100.00
        [codex]=100.00
        [gemini]=50.00
    )
    local -A req_limits=(
        [claude]=1000
        [codex]=3000
        [gemini]=100
    )
    local -A tok_limits=(
        [claude]=300000
        [codex]=500000
        [gemini]=100000
    )

    for provider in claude codex gemini; do
        local usage_file="$config_dir/${provider}_usage.json"
        if [[ ! -f "$usage_file" ]]; then
            cat > "$usage_file" <<EOF
{
  "timestamp": "$timestamp",
  "requests_used": 0,
  "requests_limit": ${req_limits[$provider]},
  "requests_percent": 0,
  "tokens_used": 0,
  "tokens_limit": ${tok_limits[$provider]},
  "tokens_percent": 0,
  "cost_today": 0.00,
  "daily_budget": ${budgets[$provider]},
  "session_started": "$timestamp"
}
EOF
            echo "Bootstrapped: $usage_file" >&2
        fi
    done
}
