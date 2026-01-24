#!/bin/bash
# Session end evaluation hook
# Trigger: Stop event
# Purpose: Evaluate session patterns for learning and append to learned-patterns.json

set -euo pipefail

# Determine workspace root
WORKSPACE_ROOT="${WORKSPACE_HUB:-/mnt/github/workspace-hub}"
STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
PATTERNS_FILE="${STATE_DIR}/learned-patterns.json"
SESSION_LOG_DIR="${STATE_DIR}/sessions"

# Ensure directories exist
mkdir -p "${STATE_DIR}"
mkdir -p "${SESSION_LOG_DIR}"

# Read hook input from stdin (session transcript data)
HOOK_INPUT=$(cat)

# Extract session metadata
SESSION_ID=$(echo "${HOOK_INPUT}" | jq -r '.session_id // "session-'$(date +%s)'"' 2>/dev/null || echo "session-$(date +%s)")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Initialize patterns file if it doesn't exist
if [[ ! -f "${PATTERNS_FILE}" ]]; then
    echo '{"patterns": [], "last_updated": ""}' > "${PATTERNS_FILE}"
fi

# Analyze session for patterns
# Pattern categories:
# - tool_usage: Which tools were used most frequently
# - delegation: How often Task tool was used (orchestrator pattern compliance)
# - errors: Common errors encountered
# - workflows: Repeated sequences of actions

# Extract tool usage patterns from session transcript if available
TOOL_PATTERNS=""
DELEGATION_SCORE="unknown"
ERROR_PATTERNS=""

# Try to extract patterns from hook input
if echo "${HOOK_INPUT}" | jq -e '.transcript' > /dev/null 2>&1; then
    # Count tool invocations
    TOOL_PATTERNS=$(echo "${HOOK_INPUT}" | jq -r '
        .transcript // [] |
        map(select(.type == "tool_use")) |
        group_by(.tool_name) |
        map({tool: .[0].tool_name, count: length}) |
        sort_by(-.count) |
        .[0:5]
    ' 2>/dev/null || echo "[]")

    # Calculate delegation score (Task tool usage vs direct execution)
    TASK_USES=$(echo "${HOOK_INPUT}" | jq '[.transcript[]? | select(.tool_name == "Task")] | length' 2>/dev/null || echo "0")
    TOTAL_TOOLS=$(echo "${HOOK_INPUT}" | jq '[.transcript[]? | select(.type == "tool_use")] | length' 2>/dev/null || echo "1")

    if [[ "${TOTAL_TOOLS}" -gt 0 ]]; then
        DELEGATION_SCORE=$(echo "scale=2; ${TASK_USES} * 100 / ${TOTAL_TOOLS}" | bc 2>/dev/null || echo "unknown")
        DELEGATION_SCORE="${DELEGATION_SCORE}%"
    fi

    # Extract error patterns
    ERROR_PATTERNS=$(echo "${HOOK_INPUT}" | jq -r '
        .transcript // [] |
        map(select(.type == "error" or (.content | tostring | test("error|Error|ERROR"; "i")))) |
        .[0:3] |
        map(.content // .message // "unknown error")
    ' 2>/dev/null || echo "[]")
fi

# Create new pattern entry
NEW_PATTERN=$(cat <<EOF
{
  "session_id": "${SESSION_ID}",
  "timestamp": "${TIMESTAMP}",
  "insights": {
    "delegation_score": "${DELEGATION_SCORE}",
    "tool_patterns": ${TOOL_PATTERNS:-"[]"},
    "error_patterns": ${ERROR_PATTERNS:-"[]"}
  },
  "recommendations": []
}
EOF
)

# Generate recommendations based on patterns
RECOMMENDATIONS="[]"

if [[ "${DELEGATION_SCORE}" != "unknown" ]]; then
    SCORE_NUM=$(echo "${DELEGATION_SCORE}" | tr -d '%')
    if [[ $(echo "${SCORE_NUM} < 30" | bc 2>/dev/null || echo "0") -eq 1 ]]; then
        RECOMMENDATIONS=$(echo '["Consider using Task tool more for orchestrator pattern compliance"]' | jq .)
    fi
fi

# Update pattern entry with recommendations
NEW_PATTERN=$(echo "${NEW_PATTERN}" | jq --argjson recs "${RECOMMENDATIONS}" '.recommendations = $recs')

# Append to patterns file (keep last 50 sessions)
UPDATED_PATTERNS=$(jq --argjson new "${NEW_PATTERN}" '
    .patterns = ([$new] + .patterns)[0:50] |
    .last_updated = $new.timestamp
' "${PATTERNS_FILE}")

echo "${UPDATED_PATTERNS}" > "${PATTERNS_FILE}"

# Also save session summary to sessions directory
SESSION_SUMMARY_FILE="${SESSION_LOG_DIR}/${SESSION_ID}.json"
echo "${NEW_PATTERN}" > "${SESSION_SUMMARY_FILE}"

echo "Session patterns evaluated and saved"
echo "  Patterns file: ${PATTERNS_FILE}"
echo "  Session summary: ${SESSION_SUMMARY_FILE}"
