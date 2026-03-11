#!/usr/bin/env bash
# terminal-session-report.sh — WRK-1022 monitoring gate summary
# Reads state/terminal-monitoring/sessions.jsonl and prints a report.
#
# Usage:
#   bash scripts/monitoring/terminal-session-report.sh

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_FILE="$REPO_ROOT/state/terminal-monitoring/sessions.jsonl"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "No sessions logged yet. Run terminal-session-log.sh after sessions."
  exit 0
fi

TOTAL=$(wc -l < "$LOG_FILE")
echo "=== WRK-1022 Terminal Session Report ==="
echo "Total sessions logged: $TOTAL"
echo ""

# Sessions per machine (compact JSON: "machine":"value")
echo "--- Sessions by machine ---"
grep -o '"machine":"[^"]*"' "$LOG_FILE" \
  | sed 's/"machine":"//;s/"//' | sort | uniq -c | awk '{printf "  %-25s %d sessions\n", $2, $1}'

echo ""
echo "--- Sessions by OS ---"
grep -o '"os":"[^"]*"' "$LOG_FILE" \
  | sed 's/"os":"//;s/"//' | sort | uniq -c | awk '{printf "  %-25s %d sessions\n", $2, $1}'

echo ""
echo "--- Friction events ---"
FRICTION_COUNT=$(grep -v '"friction_flags":""' "$LOG_FILE" | grep -c '"friction_flags":' || true)
if [[ "$FRICTION_COUNT" -eq 0 ]]; then
  echo "  None detected"
else
  echo "  Sessions with friction: $FRICTION_COUNT"
  grep -o '"friction_flags":"[^"]*"' "$LOG_FILE" | grep -v '""' \
    | sed 's/"friction_flags":"//;s/"//' | tr ',' '\n' | sort | uniq -c | sort -rn \
    | awk '{printf "  %-30s x%d\n", $2, $1}'
fi

echo ""
echo "--- Notes ---"
grep -o '"note":"[^"]*"' "$LOG_FILE" | grep -v '"note":""' \
  | sed 's/"note":"//;s/"//' | while read -r note; do
    echo "  - $note"
  done || echo "  No notes"

echo ""
echo "--- Close gate status ---"
LINUX_COUNT=$(grep '"os":"linux"' "$LOG_FILE" | wc -l)
WIN_COUNT=$(grep '"os":"windows-gitbash"' "$LOG_FILE" | wc -l)
TARGET=5  # sessions per platform before close
echo "  Linux    : $LINUX_COUNT / $TARGET sessions"
echo "  Windows  : $WIN_COUNT / $TARGET sessions"
if [[ "$LINUX_COUNT" -ge "$TARGET" ]] && [[ "$WIN_COUNT" -ge "$TARGET" ]]; then
  echo ""
  echo "  READY TO CLOSE — run: /work run WRK-1022"
else
  REMAINING=$(( (TARGET - LINUX_COUNT > 0 ? TARGET - LINUX_COUNT : 0) + (TARGET - WIN_COUNT > 0 ? TARGET - WIN_COUNT : 0) ))
  echo "  $REMAINING more sessions needed across platforms"
fi
