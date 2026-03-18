#!/usr/bin/env bash
# context-budget-monitor.sh — PreCompact hook: warn user to checkpoint active WRK
# Triggered automatically when Claude Code compacts context.
# WRK-1312

# Consume stdin (PreCompact pipes conversation)
cat > /dev/null

HUB="${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null)}"
ACTIVE_WRK_FILE="${HUB}/.claude/state/active-wrk"

echo ""
echo "--- CONTEXT COMPACTION --- context window is being compressed."

if [ -f "$ACTIVE_WRK_FILE" ]; then
  WRK_ID=$(cat "$ACTIVE_WRK_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$WRK_ID" ]; then
    echo "Active WRK: ${WRK_ID}"
    echo "Action: Run \`bash scripts/work-queue/checkpoint.sh\` to save progress before context is lost."
    echo "Tip: Include decisions with --decision \"your decision text\""
  else
    echo "No active WRK detected. Consider checkpointing any in-progress work."
  fi
else
  echo "No active WRK detected. Consider checkpointing any in-progress work."
fi

exit 0
