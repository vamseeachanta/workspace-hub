#!/bin/bash
#
# Provider Filter Engine
#

# This script checks the current usage of each provider and filters
# out those that have hit their rate limits or budget thresholds.

# --- Depends on jq ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it to continue." >&2
    exit 1
fi

# --- Configuration ---
# Assuming CONFIG_DIR is set by the calling script (orchestrate.sh)
CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"

# --- Function: filter_available_providers ---
#
# @return: JSON array of available provider names
#
filter_available_providers() {
    local available_providers=()

    # --- Check CodeX Capacity ---
    local codex_usage=$(cat "$CONFIG_DIR/codex_usage.json")
    local codex_req_percent=$(echo "$codex_usage" | jq -r '.requests_percent')
    local codex_tok_percent=$(echo "$codex_usage" | jq -r '.tokens_percent')
    if (( $(echo "$codex_req_percent < 85" | bc -l) )) && (( $(echo "$codex_tok_percent < 90" | bc -l) )); then
        available_providers+=("codex")
    fi

    # --- Check Gemini Capacity ---
    local gemini_usage=$(cat "$CONFIG_DIR/gemini_usage.json")
    local gemini_req_percent=$(echo "$gemini_usage" | jq -r '.requests_percent')
    local gemini_tok_percent=$(echo "$gemini_usage" | jq -r '.tokens_percent')
    if (( $(echo "$gemini_req_percent < 80" | bc -l) )) && (( $(echo "$gemini_tok_percent < 85" | bc -l) )); then
        available_providers+=("gemini")
    fi

    # --- Check Claude Capacity ---
    local claude_usage=$(cat "$CONFIG_DIR/claude_usage.json")
    local claude_req_percent=$(echo "$claude_usage" | jq -r '.requests_percent')
    local claude_tok_percent=$(echo "$claude_usage" | jq -r '.tokens_percent')
    if (( $(echo "$claude_req_percent < 80" | bc -l) )) && (( $(echo "$claude_tok_percent < 80" | bc -l) )); then
        available_providers+=("claude")
    fi

    # --- Budget Check (Simplified) ---
    # A full budget check as per the design is complex in bash.
    # This is a simplified version. A real implementation might do this in a more robust language.
    local final_available=()
    for provider in "${available_providers[@]}"; do
        local usage_file="$CONFIG_DIR/${provider}_usage.json"
        local cost_today=$(cat "$usage_file" | jq -r '.cost_today')
        local daily_budget=$(cat "$usage_file" | jq -r '.daily_budget')
        if (( $(echo "$cost_today < $daily_budget" | bc -l) )); then
            final_available+=("$provider")
        fi
    done

    # --- Output JSON Array ---
    printf '%s\n' "${final_available[@]}" | jq -R . | jq -s .
}
