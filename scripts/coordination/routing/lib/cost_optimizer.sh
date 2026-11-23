#!/bin/bash
#
# Cost Optimization Engine
#

# This script handles cost estimation and budget tracking for the
# multi-provider orchestration system.

# --- Depends on jq ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed." >&2
    exit 1
fi

# --- Configuration ---
CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"

# --- Function: estimate_task_cost ---
# Estimates the cost of a task for a specific provider.
# @param $1: provider name
# @param $2: task description
# @return: Estimated cost in dollars (float)
estimate_task_cost() {
    local provider="$1"
    local task="$2"
    
    local profile_file="$CONFIG_DIR/${provider}_profile.json"
    if [[ ! -f "$profile_file" ]]; then
        echo "0.00"
        return
    fi
    
    # 1. Estimate tokens. 
    # heuristic: 1 word ~ 1.3 tokens. Output ~ 10x input for code/analysis.
    local word_count=$(echo "$task" | wc -w)
    local input_tokens=$(echo "$word_count * 1.3" | bc)
    
    # Simple multiplier for output estimation based on task type (naive)
    local output_multiplier=10
    if [[ "$task" == *"fix"* ]] || [[ "$task" == *"review"* ]]; then
        output_multiplier=5
    elif [[ "$task" == *"design"* ]] || [[ "$task" == *"architecture"* ]]; then
        output_multiplier=20
    fi
    
    local estimated_output_tokens=$(echo "$input_tokens * $output_multiplier" | bc)
    local total_tokens=$(echo "$input_tokens + $estimated_output_tokens" | bc)
    
    # 2. Get rates
    local cost_per_1k=$(cat "$profile_file" | jq -r '.rate_limits.cost_per_1k_tokens')
    local cost_per_req=$(cat "$profile_file" | jq -r '.rate_limits.cost_per_request')
    
    # 3. Calculate
    # cost = (tokens / 1000) * rate + request_cost
    local token_cost=$(echo "$total_tokens / 1000 * $cost_per_1k" | bc -l)
    local total_cost=$(echo "$token_cost + $cost_per_req" | bc -l)
    
    printf "%.4f" "$total_cost"
}

# --- Function: check_budget_guardrail ---
# Checks if adding the estimated cost would exceed the daily budget.
# @param $1: provider name
# @param $2: estimated cost
# @return: 0 if safe, 1 if it would exceed budget
check_budget_guardrail() {
    local provider="$1"
    local est_cost="$2"
    local usage_file="$CONFIG_DIR/${provider}_usage.json"
    
    if [[ ! -f "$usage_file" ]]; then
        return 0
    fi
    
    local cost_today=$(cat "$usage_file" | jq -r '.cost_today')
    local daily_budget=$(cat "$usage_file" | jq -r '.daily_budget')
    
    local projected_cost=$(echo "$cost_today + $est_cost" | bc -l)
    
    if (( $(echo "$projected_cost > $daily_budget" | bc -l) )); then
        return 1
    else
        return 0
    fi
}

# --- Function: check_budget_status ---
# Returns the percentage of budget used.
get_budget_usage_percent() {
    local provider="$1"
    local usage_file="$CONFIG_DIR/${provider}_usage.json"
    
    if [[ ! -f "$usage_file" ]]; then
        echo "0"
        return
    fi
    
    local cost_today=$(cat "$usage_file" | jq -r '.cost_today')
    local daily_budget=$(cat "$usage_file" | jq -r '.daily_budget')
    
    echo "scale=2; $cost_today / $daily_budget * 100" | bc -l
}

