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
CONFIG_DIR="/mnt/github/workspace-hub/config"
LOG_DIR="$SCRIPT_DIR/logs"

# --- Source Libraries ---
# Will be added as they are created
source "$LIB_DIR/task_classifier.sh"
source "$LIB_DIR/provider_filter.sh"
source "$LIB_DIR/provider_recommender.sh"
source "$LIB_DIR/cost_optimizer.sh"
source "$LIB_DIR/agent_dispatcher.sh"
source "$LIB_DIR/audit_logger.sh"

# --- Main Logic ---
main() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 \"<task_description>\""
        exit 1
    fi

    local task_description="$1"

    # --- Context Detection ---
    if [[ -n "$GEMINI_CLI" ]]; then
        echo "Context: Gemini CLI Detected"
    elif [[ -n "$CLAUDE_PROJECT_NAME" ]] || [[ -n "$CLAUDE_CLI_CONTEXT" ]]; then
        echo "Context: Claude Code Detected"
    fi
    
    echo "--- [1/5] Classifying Task ---"
    classification_json=$(classify_task "$task_description")
    primary_provider=$(echo "$classification_json" | jq -r '.primary_provider')
    echo "Primary provider determined: $primary_provider"
    
    echo "--- [2/5] Filtering Providers ---"
    available_providers_json=$(filter_available_providers)
    echo "Available providers: $(echo "$available_providers_json" | jq -c '.')"

    echo "--- [3/5] Recommending Provider ---"
    local recommendation_json=$(recommend_provider "$classification_json" "$available_providers_json" "$task_description")
    local selected_provider=$(echo "$recommendation_json" | jq -r '.provider')
    local reason=$(echo "$recommendation_json" | jq -r '.reason')
    local cost=$(echo "$recommendation_json" | jq -r '.cost_estimate')
    
    echo "Recommended Provider: $selected_provider"
    echo "Reason: $reason"
    echo "Estimated Cost: \$$cost"
    
    # --- [3.5/5] Budget Guardrail ---
    if ! check_budget_guardrail "$selected_provider" "$cost"; then
        echo "⚠️  ROLLBACK: Estimated cost (\$$cost) exceeds remaining daily budget for $selected_provider."
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
    log_recommendation "$task_description" "$classification_json" "$available_providers_json" "$recommendation_json" "$selected_agent"
    
    echo "Orchestration complete."
}

main "$@"
