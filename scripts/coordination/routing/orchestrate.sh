#!/bin/bash
#
# Multi-Provider AI Orchestration System
# Version: 1.0.0
#
# This script is the main entry point for the orchestration system.
# It takes a task description and routes it to the best provider
# based on classification, availability, and cost.

set -e
set -o pipefail

# --- Configuration ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_DIR="$SCRIPT_DIR/lib"
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/config"
LOG_DIR="$SCRIPT_DIR/logs"

# --- Source Libraries ---
# Will be added as they are created
source "$LIB_DIR/task_classifier.sh"
source "$LIB_DIR/provider_filter.sh"
source "$LIB_DIR/provider_recommender.sh"
source "$LIB_DIR/cost_optimizer.sh"
source "$LIB_DIR/agent_dispatcher.sh"
source "$LIB_DIR/audit_logger.sh"
source "$LIB_DIR/tier_router.sh"
source "$LIB_DIR/usage_bootstrap.sh"

# --- Main Logic ---
main() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 \"<task_description>\""
        exit 1
    fi

    local task_description="$1"

    # --- Bootstrap usage tracking files ---
    bootstrap_usage_files

    # --- Context Detection ---
    if [[ -n "$GEMINI_CLI" ]]; then
        echo "Context: Gemini CLI Detected"
    elif [[ -n "$CLAUDE_PROJECT_NAME" ]] || [[ -n "$CLAUDE_CLI_CONTEXT" ]]; then
        echo "Context: Claude Code Detected"
    fi
    
    echo "--- [1/5] Classifying Task (10-dimension) ---"
    classification_json=$(classify_task "$task_description")
    primary_provider=$(echo "$classification_json" | jq -r '.primary_provider')
    tier=$(echo "$classification_json" | jq -r '.tier')
    confidence=$(echo "$classification_json" | jq -r '.confidence')
    echo "Tier: $tier | Provider: $primary_provider | Confidence: $confidence"
    
    echo "--- [2/5] Filtering Providers ---"
    available_providers_json=$(filter_available_providers)
    echo "Available providers: $(echo "$available_providers_json" | jq -c '.')"

    echo "--- [3/5] Routing by Tier ---"
    local routing_json=$(route_by_tier "$tier" "$primary_provider" "$confidence")
    local selected_provider=$(echo "$routing_json" | jq -r '.provider')
    local reason=$(echo "$routing_json" | jq -r '.reason')
    local auto_route=$(echo "$routing_json" | jq -r '.auto_route')

    # Cost estimation
    local cost=$(estimate_task_cost "$selected_provider" "$task_description")

    echo "Routed to: $selected_provider"
    echo "Reason: $reason"
    echo "Auto-route: $auto_route | Estimated Cost: \$$cost"
    
    # --- [3.5/5] Budget Guardrail ---
    if ! check_budget_guardrail "$selected_provider" "$cost"; then
        echo "ROLLBACK: Estimated cost (\$$cost) exceeds remaining daily budget for $selected_provider."
        echo "Please increase budget in config/${selected_provider}_usage.json or defer task."
        exit 2
    fi
    
    echo "--- [4/5] Dispatching to Agent ---"
    local selected_agent=$(select_agent "$selected_provider" "$task_description")
    echo "Selected Agent: $selected_agent"
    
    echo "--- [5/5] Executing Task ---"
    local dispatch_cmd=$(get_dispatch_command "$selected_provider" "$selected_agent" "$task_description")
    echo "Execution Command: $dispatch_cmd"
    
    # --- Logging ---
    log_recommendation "$task_description" "$classification_json" "$available_providers_json" "$routing_json" "$selected_agent"
    
    echo "Orchestration complete."
}

main "$@"
