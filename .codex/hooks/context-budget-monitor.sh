#!/usr/bin/env bash
# context-budget-monitor.sh — PreCompact hook: warn about context compaction
# Triggered automatically when Claude Code compacts context.

# Consume stdin (PreCompact pipes conversation)
cat > /dev/null

echo ""
echo "--- CONTEXT COMPACTION --- context window is being compressed."
echo "Consider saving progress. If in a GSD workflow, use /gsd:pause-work."

exit 0
