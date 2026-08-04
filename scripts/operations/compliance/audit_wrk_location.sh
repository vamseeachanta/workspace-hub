#!/usr/bin/env bash

# ABOUTME: Identify WRK items outside the central work-queue
# ABOUTME: Supports warn/gate mode and JSON reporting

set -euo pipefail

CENTRAL_QUEUE=".claude/work-queue"
MODE="warn"
REPORT_FILE=""
EXIT_CODE=0

usage() {
  cat << USAGE
Usage: $(basename "$0") [--mode warn|gate] [--report <file>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-warn}"; shift 2 ;;
    --report) REPORT_FILE="${2:-}"; shift 2 ;;
    --scope|--base-ref) shift 2 ;; # Ignore for now as location audit is global
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

echo "Checking for WRK files outside $CENTRAL_QUEUE..."

# Find all WRK-*.md files, excluding:
# - central queue
# - specs/wrk (legitimate spec location)
# - _archive
# - node_modules
# - .git
# - any scripts/review/results directories
WRK_FILES=$(find . -name "WRK-*.md" \
  -not -path "./$CENTRAL_QUEUE/*" \
  -not -path "./specs/wrk/*" \
  -not -path "./_archive/*" \
  -not -path "*/node_modules/*" \
  -not -path "./.git/*" \
  -not -path "*/scripts/review/results/*" \
  -type f)

ISSUES=()
for f in $WRK_FILES; do
  ISSUES+=("$(echo $f | sed 's|^\./||')")
done

ISSUE_COUNT=${#ISSUES[@]}

if [ $ISSUE_COUNT -gt 0 ]; then
    echo "Found $ISSUE_COUNT WRK files in prohibited locations:"
    for issue in "${ISSUES[@]}"; do
      echo "  - $issue"
    done
    if [[ "$MODE" == "gate" ]]; then
      EXIT_CODE=1
    fi
else
    echo "No misplaced WRK files found."
fi

if [[ -n "$REPORT_FILE" ]]; then
  # Build simple JSON report
  echo "{" > "$REPORT_FILE"
  echo "  \"issue_count\": $ISSUE_COUNT," >> "$REPORT_FILE"
  echo "  \"issues\": [" >> "$REPORT_FILE"
  for i in "${!ISSUES[@]}"; do
    comma=","
    if [[ $i -eq $((ISSUE_COUNT-1)) ]]; then comma=""; fi
    echo "    \"${ISSUES[$i]}\"$comma" >> "$REPORT_FILE"
  done
  echo "  ]" >> "$REPORT_FILE"
  echo "}" >> "$REPORT_FILE"
fi

exit $EXIT_CODE
