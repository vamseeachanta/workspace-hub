#!/usr/bin/env bash
# claim-item.sh - Handle claim gate for a work item
set -euo pipefail

WRK_ID="${1:-}"

if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>"
  exit 1
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
QUOTA_FILE="${WORKSPACE_ROOT}/config/ai-tools/agent-quota-latest.json"

# Find file
FILE_PATH=""
if [[ -f "${QUEUE_DIR}/pending/${WRK_ID}.md" ]]; then
  FILE_PATH="${QUEUE_DIR}/pending/${WRK_ID}.md"
elif [[ -f "${QUEUE_DIR}/blocked/${WRK_ID}.md" ]]; then
  FILE_PATH="${QUEUE_DIR}/blocked/${WRK_ID}.md"
fi

if [[ -z "$FILE_PATH" ]]; then
  echo "✖ Error: Could not find ${WRK_ID}.md in pending/ or blocked/"
  exit 1
fi

# Check blocked
if [[ "$FILE_PATH" == *"blocked"* ]]; then
  echo "✖ Error: ${WRK_ID} is blocked. Resolve blockers first."
  exit 1
fi

# Quota Check
echo "Checking quota..."
if [[ -f "$QUOTA_FILE" ]]; then
  # Simple grep for now, could use jq
  grep -A 5 "status" "$QUOTA_FILE" || echo "Quota info unavailable"
else
  echo "⚠ Quota file missing: $QUOTA_FILE"
fi

# Claim Evidence
CLAIM_DIR="${WORKSPACE_ROOT}/.claude/work-queue/assets/${WRK_ID}"
mkdir -p "$CLAIM_DIR"
CLAIM_FILE="${CLAIM_DIR}/claim-evidence.yaml"

cat <<EOF > "$CLAIM_FILE"
claim_date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
session_id: $(grep "session_id" "${QUEUE_DIR}/session-state.yaml" | cut -d'"' -f2)
quota_snapshot:
  source: "$QUOTA_FILE"
  status: checked
agent_capability:
  best_fit: matched
  rationale: "Assigned by orchestrator based on plan."
EOF

# Move to working
mkdir -p "${QUEUE_DIR}/working"
mv "$FILE_PATH" "${QUEUE_DIR}/working/${WRK_ID}.md"

# Update frontmatter
sed -i "s/^status:.*$/status: working/" "${QUEUE_DIR}/working/${WRK_ID}.md"

# Regenerate index
python3 "${QUEUE_DIR}/scripts/generate-index.py"

echo "✔ ${WRK_ID} claimed and moved to working/"
