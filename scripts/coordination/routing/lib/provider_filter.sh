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

# Single routing resolver (#3205) — the only forbid-policy interpreter. Define
# _resolver only if a sibling lib (tier_router.sh) hasn't already.
if ! declare -F _resolver >/dev/null 2>&1; then
    RESOLVER="${RESOLVER:-$(dirname "$CONFIG_DIR")/scripts/ai/routing_resolver.py}"
    _resolver() {
        if command -v uv >/dev/null 2>&1; then
            uv run --quiet "$RESOLVER" "$@"
        else
            python3 "$RESOLVER" "$@"
        fi
    }
fi

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

    # --- Cost-ceiling enforcement (#3205) ---
    # Drop providers forbidden for the active execution context via the single
    # resolver (no re-implemented forbid logic). --no-fallback: report genuine
    # availability, never re-add an unavailable provider. Fail closed on a bad
    # context. Interactive path (no ROUTE_CONTEXT) is unchanged.
    # Validate + filter whenever a context is set — even if the available set is
    # empty, so an unknown context still fails closed (review r3-F2). With an
    # empty input, --filter "" returns [] for a valid context and exit 3 for a
    # bad one.
    if [[ -n "${ROUTE_CONTEXT:-}" ]]; then
        local _csv; _csv="$(IFS=,; echo "${final_available[*]:-}")"
        local _filtered
        if ! _filtered="$(_resolver --context "$ROUTE_CONTEXT" --filter "$_csv" --no-fallback)"; then
            echo "filter_available_providers: unknown/invalid context '$ROUTE_CONTEXT' — aborting (fail closed)" >&2
            return 3
        fi
        final_available=()
        local _line
        while IFS= read -r _line; do [[ -n "$_line" ]] && final_available+=("$_line"); done <<< "$_filtered"
    fi

    # --- Output JSON Array ---
    if [[ ${#final_available[@]} -eq 0 ]]; then
        echo "[]"
    else
        printf '%s\n' "${final_available[@]}" | jq -R . | jq -s .
    fi
}
