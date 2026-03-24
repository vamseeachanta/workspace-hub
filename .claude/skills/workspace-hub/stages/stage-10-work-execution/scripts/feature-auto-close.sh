#!/usr/bin/env bash
# feature-auto-close.sh — After a child WRK archives, check if parent
# feature can close.
# Usage: feature-auto-close.sh <WRK-NNN>  (the just-archived child)
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel)}"
QUEUE_DIR="${WORK_QUEUE_ROOT:-${WORKSPACE_ROOT}/.claude/work-queue}"

ITEM_ID="${1:-}"
if [[ -z "$ITEM_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>" >&2
  exit 1
fi

# Normalize ID format
[[ "$ITEM_ID" =~ ^WRK- ]] || ITEM_ID="WRK-${ITEM_ID}"

# Find the child's WRK file (check archive/ first since it was just archived)
CHILD_FILE=""
for dir in $(find "${QUEUE_DIR}/archive" -mindepth 1 -maxdepth 1 -type d 2>/dev/null) "${QUEUE_DIR}/archive"; do
  if [[ -f "${dir}/${ITEM_ID}.md" ]]; then
    CHILD_FILE="${dir}/${ITEM_ID}.md"
    break
  fi
done
# Fallback: check other directories
if [[ -z "$CHILD_FILE" ]]; then
  for dir in working pending blocked done; do
    if [[ -f "${QUEUE_DIR}/${dir}/${ITEM_ID}.md" ]]; then
      CHILD_FILE="${QUEUE_DIR}/${dir}/${ITEM_ID}.md"
      break
    fi
  done
fi

if [[ -z "$CHILD_FILE" ]]; then
  # Item not found — not necessarily an error, exit silently
  exit 0
fi

# Parse parent: field from frontmatter
PARENT_ID=$(grep -m1 '^parent:' "$CHILD_FILE" \
  | sed 's/^parent:[[:space:]]*//' \
  | tr -d '"' \
  | xargs 2>/dev/null || true)

if [[ -z "$PARENT_ID" ]]; then
  # Not a child WRK — exit silently
  exit 0
fi

# Normalize parent ID
[[ "$PARENT_ID" =~ ^WRK- ]] || PARENT_ID="WRK-${PARENT_ID}"

# Run feature-close-check on the parent
FEATURE_CLOSE_CHECK="${WORKSPACE_ROOT}/scripts/work-queue/feature-close-check.sh"
if [[ ! -x "$FEATURE_CLOSE_CHECK" ]]; then
  echo "feature-auto-close: feature-close-check.sh not found or not executable" >&2
  exit 0
fi

check_exit=0
bash "$FEATURE_CLOSE_CHECK" "$PARENT_ID" || check_exit=$?

if [[ "$check_exit" -eq 0 ]]; then
  echo "All children of ${PARENT_ID} archived. Auto-closing feature WRK."
  CLOSE_ITEM="${WORKSPACE_ROOT}/scripts/work-queue/close-item.sh"
  if [[ -x "$CLOSE_ITEM" ]]; then
    bash "$CLOSE_ITEM" "$PARENT_ID" || \
      echo "feature-auto-close: close-item.sh failed for ${PARENT_ID} (may need manual evidence)" >&2
  else
    echo "feature-auto-close: close-item.sh not found" >&2
  fi
else
  echo "Parent ${PARENT_ID} still has unarchived children."
fi
