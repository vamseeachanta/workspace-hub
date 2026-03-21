#!/usr/bin/env bash
# WRK-1389 L3 Hook: Enforce dispatch-run.sh before group runners
#
# Blocks direct calls to run-plan.sh, run-execute.sh, run-review-plan.sh,
# run-close.sh unless dispatch-run.sh has been called first (breadcrumb exists).
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse (Bash matcher).
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)

# Only intercept group runner calls
if ! echo "$COMMAND" | grep -qP 'run-(plan|execute|review-plan|close)\.sh' 2>/dev/null; then
    exit 0
fi

# Allow dispatch-run.sh itself (it calls nothing, just prints)
if echo "$COMMAND" | grep -qP 'dispatch-run\.sh' 2>/dev/null; then
    exit 0
fi

# Extract WRK ID from command
WRK_ID=$(echo "$COMMAND" | grep -oP 'WRK-\d+' | head -1)
if [[ -z "$WRK_ID" ]]; then
    exit 0  # Can't determine WRK — allow (other hooks will catch)
fi

# Check for dispatch breadcrumb
BREADCRUMB="$REPO_ROOT/.claude/state/dispatch-${WRK_ID}"
if [[ -f "$BREADCRUMB" ]]; then
    exit 0  # Dispatch was called — allow
fi

echo "BLOCKED: Run dispatch-run.sh before calling group runners directly." >&2
echo "  → bash scripts/work-queue/dispatch-run.sh $WRK_ID" >&2
echo "  Then follow its output." >&2
exit 2
