#!/bin/bash
# Pre-compact session memory persistence hook
# Trigger: PreCompact event
# Purpose: Save session state to .claude/state/session-memory.json

set -euo pipefail

# Determine workspace root
WORKSPACE_ROOT="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../../.." && pwd)}"
STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
STATE_FILE="${STATE_DIR}/session-memory.json"
SPECS_DIR="${WORKSPACE_ROOT}/specs/modules"

# Ensure state directory exists
mkdir -p "${STATE_DIR}"

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract session context from hook input
SESSION_ID=$(echo "${HOOK_INPUT}" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")

# Find active plan (most recently modified .md in specs/modules)
ACTIVE_PLAN=""
if [[ -d "${SPECS_DIR}" ]]; then
    ACTIVE_PLAN=$(find "${SPECS_DIR}" -name "*.md" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2- || echo "")
    # Convert to relative path from workspace root
    if [[ -n "${ACTIVE_PLAN}" ]]; then
        ACTIVE_PLAN="${ACTIVE_PLAN#${WORKSPACE_ROOT}/}"
    fi
fi

# Parse completed and pending tasks from active plan
COMPLETED_TASKS="[]"
PENDING_TASKS="[]"

if [[ -n "${ACTIVE_PLAN}" && -f "${WORKSPACE_ROOT}/${ACTIVE_PLAN}" ]]; then
    # Extract completed tasks (lines with [x])
    COMPLETED_TASKS=$(grep -E '^\s*-\s*\[x\]' "${WORKSPACE_ROOT}/${ACTIVE_PLAN}" 2>/dev/null | \
        sed 's/.*\[x\]\s*//' | \
        jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo "[]")

    # Extract pending tasks (lines with [ ])
    PENDING_TASKS=$(grep -E '^\s*-\s*\[\s\]' "${WORKSPACE_ROOT}/${ACTIVE_PLAN}" 2>/dev/null | \
        sed 's/.*\[\s\]\s*//' | \
        jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo "[]")
fi

# Estimate context budget used (placeholder - actual value would come from Claude internals)
# This is a heuristic based on hook being called during compaction
CONTEXT_BUDGET_USED="45%"

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create session memory JSON
cat > "${STATE_FILE}" <<EOF
{
  "session_id": "${SESSION_ID}",
  "active_plan": "${ACTIVE_PLAN}",
  "completed_tasks": ${COMPLETED_TASKS},
  "pending_tasks": ${PENDING_TASKS},
  "context_budget_used": "${CONTEXT_BUDGET_USED}",
  "timestamp": "${TIMESTAMP}",
  "workspace": "${WORKSPACE_ROOT}"
}
EOF

# Validate JSON was created correctly
if ! jq . "${STATE_FILE}" > /dev/null 2>&1; then
    echo "Warning: Invalid JSON in session-memory.json" >&2
    # Create minimal valid fallback
    cat > "${STATE_FILE}" <<EOF
{
  "session_id": "${SESSION_ID}",
  "active_plan": "",
  "completed_tasks": [],
  "pending_tasks": [],
  "context_budget_used": "unknown",
  "timestamp": "${TIMESTAMP}",
  "workspace": "${WORKSPACE_ROOT}"
}
EOF
fi

echo "Session memory saved to ${STATE_FILE}"
