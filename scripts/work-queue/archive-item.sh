#!/usr/bin/env bash
# archive-item.sh - Move completed item to archive with metadata
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

ITEM_ID="${1:?Usage: archive-item.sh WRK-NNN}"

# Normalize ID format
[[ "$ITEM_ID" =~ ^WRK- ]] || ITEM_ID="WRK-${ITEM_ID}"

# Find the item file in working/ or pending/
ITEM_FILE=""
for dir in working pending blocked; do
  MATCH=$(find "${QUEUE_DIR}/${dir}" -name "${ITEM_ID}-*.md" 2>/dev/null | head -1)
  if [[ -n "$MATCH" ]]; then
    ITEM_FILE="$MATCH"
    break
  fi
done

if [[ -z "$ITEM_FILE" ]]; then
  echo "Error: Item ${ITEM_ID} not found in pending/working/blocked" >&2
  exit 1
fi

# Create archive directory for current month
ARCHIVE_DIR="${QUEUE_DIR}/archive/$(date +%Y-%m)"
mkdir -p "$ARCHIVE_DIR"

BASENAME=$(basename "$ITEM_FILE")
ARCHIVE_PATH="${ARCHIVE_DIR}/${BASENAME}"

# Read current content
CONTENT=$(cat "$ITEM_FILE")

# Calculate duration if claimed_at exists
CLAIMED_AT=$(grep "claimed_at:" "$ITEM_FILE" | head -1 | sed 's/claimed_at: *//' | tr -d '"' || echo "")
DURATION=""
if [[ -n "$CLAIMED_AT" ]]; then
  CLAIMED_TS=$(date -d "$CLAIMED_AT" +%s 2>/dev/null || echo "0")
  NOW_TS=$(date +%s)
  if [[ "$CLAIMED_TS" -gt 0 ]]; then
    DURATION_SECS=$((NOW_TS - CLAIMED_TS))
    DURATION=$((DURATION_SECS / 60))
  fi
fi

# Update frontmatter with completion metadata
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
{
  echo "$CONTENT" | sed \
    -e "s/^status: .*/status: done/" \
    -e "/^---$/,/^---$/ { /^blocked_by:/a\\
completed_at: ${NOW_ISO}
}"
} > "$ARCHIVE_PATH"

# If duration was calculated, add it
if [[ -n "$DURATION" ]]; then
  sed -i "/^completed_at:/a duration_minutes: ${DURATION}" "$ARCHIVE_PATH" 2>/dev/null || true
fi

# Remove from source directory
rm "$ITEM_FILE"

echo "Archived: ${ITEM_ID} -> archive/$(date +%Y-%m)/${BASENAME}"

# Update state.yaml
STATE_FILE="${QUEUE_DIR}/state.yaml"
if [[ -f "$STATE_FILE" ]]; then
  # Increment archived count
  CURRENT=$(grep "archived_count:" "$STATE_FILE" | grep -oE '[0-9]+' || echo "0")
  NEW_COUNT=$((CURRENT + 1))
  sed -i "s/archived_count: .*/archived_count: ${NEW_COUNT}/" "$STATE_FILE" 2>/dev/null || true
fi
