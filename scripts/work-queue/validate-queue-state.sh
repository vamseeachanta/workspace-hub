#!/usr/bin/env bash
# validate-queue-state.sh - Lint work-queue state and status
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

FAILED=0
ERRORS=()
WARNINGS=()

# Allowed status values
ALLOWED_STATUSES=("pending" "working" "done" "archived" "blocked" "failed")
LEGACY_STATUSES=("complete" "completed" "closed")

check_file() {
  local file="$1"
  local expected_status="$2"
  local filename=$(basename "$file")
  
  # Read status from frontmatter
  local status=$(grep "^status:" "$file" | head -n1 | cut -d':' -f2 | xargs)
  
  if [[ -z "$status" ]]; then
    ERRORS+=("Missing status in $filename")
    return
  fi

  # Check for legacy status
  for legacy in "${LEGACY_STATUSES[@]}"; do
    if [[ "$status" == "$legacy" ]]; then
      WARNINGS+=("Legacy status '$status' in $filename")
      return
    fi
  done

  # Check for allowed status
  local found=0
  for allowed in "${ALLOWED_STATUSES[@]}"; do
    if [[ "$status" == "$allowed" ]]; then
      found=1
      break
    fi
  done
  
  if [[ $found -eq 0 ]]; then
    ERRORS+=("Invalid status '$status' in $filename")
  fi

  # Check folder/status mismatch
  if [[ -n "$expected_status" && "$status" != "$expected_status" ]]; then
    ERRORS+=("Mismatch: $filename has status '$status' but is in '$expected_status/' folder")
  fi
}

# Scan folders
echo "Scanning work-queue for inconsistencies..."

# Pending
if [[ -d "${QUEUE_DIR}/pending" ]]; then
  for file in "${QUEUE_DIR}/pending"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    check_file "$file" "pending"
  done
fi

# Working
if [[ -d "${QUEUE_DIR}/working" ]]; then
  for file in "${QUEUE_DIR}/working"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    check_file "$file" "working"
  done
fi

# Blocked
if [[ -d "${QUEUE_DIR}/blocked" ]]; then
  for file in "${QUEUE_DIR}/blocked"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    check_file "$file" "blocked"
  done
fi

# Done
if [[ -d "${QUEUE_DIR}/done" ]]; then
  for file in "${QUEUE_DIR}/done"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    check_file "$file" "done"
  done
fi

# Archive (recursive)
if [[ -d "${QUEUE_DIR}/archive" ]]; then
  while IFS= read -r file; do
    check_file "$file" "archived"
  done < <(find "${QUEUE_DIR}/archive" -name "WRK-*.md")
fi

# Report
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo -e "
Errors found (${#ERRORS[@]}):"
  for err in "${ERRORS[@]}"; do
    echo "  ✖ $err"
  done
  FAILED=1
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo -e "
Warnings found (${#WARNINGS[@]}):"
  for warn in "${WARNINGS[@]}"; do
    echo "  ⚠ $warn"
  done
fi

if [[ $FAILED -eq 0 ]]; then
  echo -e "
Queue state validation passed."
  exit 0
else
  echo -e "
Queue state validation failed."
  exit 1
fi
