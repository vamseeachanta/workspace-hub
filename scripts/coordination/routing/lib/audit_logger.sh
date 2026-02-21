#!/bin/bash
#
# Audit Trail Logger
#

# This script logs orchestration decisions and outcomes to a JSONL file.

# --- Depends on jq ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed." >&2
    exit 1
fi

# --- Configuration ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Correctly resolve LOG_DIR relative to the script location if not set
LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/../logs}"
LOG_FILE="$LOG_DIR/provider_recommendations.jsonl"

# --- Function: log_recommendation ---
# Logs the full details of a recommendation decision.
# Arguments are passed as named JSON strings for safety
log_recommendation() {
    local task="$1"
    local classification="$2"
    local available_providers="$3"
    local recommendation="$4" # Includes provider, reason, cost
    local agent="$5"
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
        # Construct the log entry using jq to ensure valid JSON
        jq -c -n \
          --arg timestamp "$timestamp" \
          --arg task "$task" \
          --argjson classification "$classification" \
          --argjson available "$available_providers" \
          --argjson recommendation "$recommendation" \
          --arg agent "$agent" \
          '{
            timestamp: $timestamp,
            task: $task,
            task_classification: $classification,
            available_providers: $available,
            recommendation: $recommendation,
            agent_assigned: $agent
          }' >> "$LOG_FILE"
    }
