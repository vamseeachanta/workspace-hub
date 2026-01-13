#!/bin/bash
#
# Adaptive Selection Optimizer
#
# Analyzes feedback and suggests adjustments to keyword weights.

FEEDBACK_FILE="/mnt/github/workspace-hub/scripts/routing/logs/feedback.jsonl"
LOG_FILE="/mnt/github/workspace-hub/scripts/routing/logs/provider_recommendations.jsonl"

if [[ ! -f "$FEEDBACK_FILE" ]]; then
    echo "No feedback data available yet."
    exit 0
fi

echo "--- Analyzing Feedback for Adaptive Optimization ---"

# Find low-rated recommendations (Rating < 3)
low_ratings=$(jq -r 'select(.rating < 3) | .target_recommendation_ts' "$FEEDBACK_FILE")

if [[ -z "$low_ratings" ]]; then
    echo "No low ratings found. Classification weights appear optimal."
    exit 0
fi

for ts in $low_ratings; do
    # Find the corresponding task and provider
    entry=$(grep "$ts" "$LOG_FILE")
    task=$(echo "$entry" | jq -r '.task')
    provider=$(echo "$entry" | jq -r '.recommendation.provider')
    
    echo "Optimization Opportunity Found:"
    echo "  Task: \"$task\""
    echo "  Provider: $provider (Rated Low)"
    
    # Simple heuristic suggestion
    echo "  Suggestion: Reduce weights for keywords found in this task for $provider,"
    echo "              or increase weights for fallback providers."
done
