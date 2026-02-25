#!/usr/bin/env bash
# queue-report.sh - Generate summary for reflect integration
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Get basic counts
PENDING=$(find "${QUEUE_DIR}/pending" -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
WORKING=$(find "${QUEUE_DIR}/working" -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
BLOCKED=$(find "${QUEUE_DIR}/blocked" -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')

# Archived this month
MONTH_DIR="${QUEUE_DIR}/archive/$(date +%Y-%m)"
ARCHIVED_MONTH=0
[[ -d "$MONTH_DIR" ]] && ARCHIVED_MONTH=$(find "$MONTH_DIR" -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ') || true

# Stale blocked items (>7 days)
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

# High priority pending
HIGH=0
[[ -d "${QUEUE_DIR}/pending" ]] && HIGH=$(find "${QUEUE_DIR}/pending" -maxdepth 1 -name "WRK-*.md" -exec grep -l "priority: high" {} + 2>/dev/null | wc -l | tr -d ' ') || true

# Failed items
FAILED=0
[[ -d "${QUEUE_DIR}/working" ]] && FAILED=$(find "${QUEUE_DIR}/working" -maxdepth 1 -name "WRK-*.md" -exec grep -l "status: failed" {} + 2>/dev/null | wc -l | tr -d ' ') || true

# Complexity breakdown
SIMPLE=0; MEDIUM=0; COMPLEX=0
for dir in pending working blocked; do
  [[ -d "${QUEUE_DIR}/${dir}" ]] || continue
  SIMPLE=$((SIMPLE + $(find "${QUEUE_DIR}/${dir}" -maxdepth 1 -name "WRK-*.md" -exec grep -l "complexity: simple" {} + 2>/dev/null | wc -l | tr -d ' ')))
  MEDIUM=$((MEDIUM + $(find "${QUEUE_DIR}/${dir}" -maxdepth 1 -name "WRK-*.md" -exec grep -l "complexity: medium" {} + 2>/dev/null | wc -l | tr -d ' ')))
  COMPLEX=$((COMPLEX + $(find "${QUEUE_DIR}/${dir}" -maxdepth 1 -name "WRK-*.md" -exec grep -l "complexity: complex" {} + 2>/dev/null | wc -l | tr -d ' ')))
done

# Output
if [[ "${1:-}" == "--json" ]]; then
  cat <<EOF
{
  "pending": $PENDING,
  "working": $WORKING,
  "blocked": $BLOCKED,
  "stale_blocked": $STALE,
  "failed": $FAILED,
  "archived_this_month": $ARCHIVED_MONTH,
  "high_priority": $HIGH,
  "complexity": {
    "simple": $SIMPLE,
    "medium": $MEDIUM,
    "complex": $COMPLEX
  }
}
EOF
else
  echo "Work Queue Report"
  echo "═══════════════════"
  echo ""
  echo "Active Queue:"
  echo "  Pending:  $PENDING (${HIGH} high priority)"
  echo "  Working:  $WORKING"
  echo "  Blocked:  $BLOCKED (${STALE} stale)"
  [[ $FAILED -gt 0 ]] && echo "  Failed:   $FAILED ⚠" || true
  echo ""
  echo "This Month:"
  echo "  Archived: $ARCHIVED_MONTH"
  echo ""
  echo "Complexity:"
  echo "  Simple:  $SIMPLE | Medium: $MEDIUM | Complex: $COMPLEX"
fi
