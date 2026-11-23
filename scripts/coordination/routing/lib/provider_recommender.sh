#!/bin/bash
#
# Provider Recommendation Engine
#

# This script selects the best provider from the available pool based on
# the task classification and cost optimization logic.

# --- Depends on jq ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed." >&2
    exit 1
fi

# --- Configuration ---
# Source cost optimizer if not already sourced
if [[ "$(type -t estimate_task_cost)" != "function" ]]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    source "$SCRIPT_DIR/cost_optimizer.sh"
fi

# --- Function: recommend_provider ---
# @param $1: classification_json
# @param $2: available_providers_json (array of strings)
# @param $3: task_description
# @return: JSON object with recommendation details
recommend_provider() {
    local classification_json="$1"
    local available_json="$2"
    local task="$3"
    
    local primary=$(echo "$classification_json" | jq -r '.primary_provider')
    
    # 1. Determine Candidates based on classification scores
    # (In a real app, we'd sort all_scores, here we hardcode the logic from the design)
    local candidates=()
    candidates+=("$primary")
    
    # Simple fallback logic: if primary is claude, fallback is codex then gemini, etc.
    # This should ideally come from the profile 'fallback_order' but for simplicity:
    if [[ "$primary" == "claude" ]]; then
        candidates+=("codex" "gemini")
    elif [[ "$primary" == "codex" ]]; then
        candidates+=("gemini" "claude")
    else # gemini
        candidates+=("codex" "claude")
    fi
    
    # 2. Find first candidate that is available
    local chosen_provider=""
    local reason=""
    
    for candidate in "${candidates[@]}"; do
        # Check availability
        if echo "$available_json" | jq -e ". | index(\"$candidate\")" > /dev/null; then
            chosen_provider="$candidate"
            if [[ "$candidate" == "$primary" ]]; then
                reason="Primary provider available"
            else
                reason="Primary blocked, using fallback"
            fi
            break
        fi
    done
    
    # 3. Emergency Fallback (if all blocked)
    if [[ -z "$chosen_provider" ]]; then
        # Pick the cheapest one (Gemini usually)
        chosen_provider="gemini" 
        reason="Emergency: All providers blocked. Using default."
    fi
    
    # 4. Cost Estimation
    local cost_est=$(estimate_task_cost "$chosen_provider" "$task")
    
    # 5. Output JSON
    jq -n \
      --arg provider "$chosen_provider" \
      --arg reason "$reason" \
      --arg cost "$cost_est" \
      '{ 
        "provider": $provider,
        "reason": $reason,
        "cost_estimate": $cost
      }'
}
