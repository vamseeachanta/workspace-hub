#!/bin/bash
#
# Feedback Collection Tool
#
# Usage: ./feedback.sh <task_id_or_timestamp> <rating_1_to_5> [comment]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/provider_recommendations.jsonl"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <timestamp> <rating_1_5> [comment]"
    exit 1
fi

TIMESTAMP="$1"
RATING="$2"
COMMENT="$3"

# Update the JSONL entry with feedback
# This is tricky with JSONL. A simple way is to append a new feedback entry 
# or use a separate file. For simplicity, we'll append to a feedback.jsonl.

FEEDBACK_FILE="$SCRIPT_DIR/logs/feedback.jsonl"

jq -n \
  --arg ts "$TIMESTAMP" \
  --argjson r "$RATING" \
  --arg c "$COMMENT" \
  '{ 
    timestamp: (date -u +"%Y-%m-%dT%H:%M:%SZ"),
    target_recommendation_ts: $ts,
    rating: $r,
    comment: $c
  }' >> "$FEEDBACK_FILE"

echo "Feedback recorded. Thank you!"
