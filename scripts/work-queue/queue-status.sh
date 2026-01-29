#!/usr/bin/env bash
# queue-status.sh - Report counts per queue state
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

# Count items per state
count_items() {
  local dir="$1"
  if [[ -d "${QUEUE_DIR}/${dir}" ]]; then
    find "${QUEUE_DIR}/${dir}" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' '
  else
    echo "0"
  fi
}

PENDING=$(count_items "pending")
WORKING=$(count_items "working")
BLOCKED=$(count_items "blocked")

# Count archived items (all subdirs)
ARCHIVED=0
if [[ -d "${QUEUE_DIR}/archive" ]]; then
  ARCHIVED=$(find "${QUEUE_DIR}/archive" -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
fi

TOTAL=$((PENDING + WORKING + BLOCKED))

# Check for stale blocked items (>7 days)
STALE=0
if [[ -d "${QUEUE_DIR}/blocked" ]]; then
  shopt -s nullglob
  SEVEN_DAYS_AGO=$(date -d "7 days ago" +%s 2>/dev/null || date -v-7d +%s 2>/dev/null || echo "0")
  for file in "${QUEUE_DIR}/blocked"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    FILE_TIME=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo "0")
    (( FILE_TIME < SEVEN_DAYS_AGO )) && ((STALE++)) || true
  done
  shopt -u nullglob
fi

# Check for high priority items
HIGH_PRIORITY=0
if [[ -d "${QUEUE_DIR}/pending" ]]; then
  HIGH_PRIORITY=$(find "${QUEUE_DIR}/pending" -maxdepth 1 -name "WRK-*.md" -exec grep -l "priority: high" {} + 2>/dev/null | wc -l | tr -d ' ')
fi

# Output format depends on argument
if [[ "${1:-}" == "--json" ]]; then
  cat <<EOF
{
  "pending": $PENDING,
  "working": $WORKING,
  "blocked": $BLOCKED,
  "archived": $ARCHIVED,
  "total_active": $TOTAL,
  "stale_blocked": $STALE,
  "high_priority": $HIGH_PRIORITY
}
EOF
elif [[ "${1:-}" == "--oneline" ]]; then
  echo "P:${PENDING} W:${WORKING} B:${BLOCKED} A:${ARCHIVED} (${STALE} stale)"
else
  echo "Work Queue Status"
  echo "================="
  echo "Pending:    $PENDING"
  echo "Working:    $WORKING"
  echo "Blocked:    $BLOCKED"
  echo "Archived:   $ARCHIVED"
  echo "─────────────────"
  echo "Active:     $TOTAL"
  [[ $HIGH_PRIORITY -gt 0 ]] && echo "High Priority: $HIGH_PRIORITY" || true
  [[ $STALE -gt 0 ]] && echo "Stale (>7d):   $STALE ⚠" || true
fi
