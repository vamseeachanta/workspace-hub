#!/usr/bin/env bash
# WRK-1316 L3 Hook: Block git commit without stage timing evidence
#
# If an active WRK exists, at least one stage-timing-*.yaml must be present.
# This ensures the agent actually ran start_stage.py (not just coded directly).
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)

# Only check git commit commands
if ! echo "$COMMAND" | grep -qP '^\s*git\s+commit' 2>/dev/null; then
    exit 0
fi

# Check for active WRK
ACTIVE_WRK_FILE="$REPO_ROOT/.claude/state/active-wrk"
if [[ ! -f "$ACTIVE_WRK_FILE" ]]; then
    exit 0  # No active WRK — allow (might be non-WRK work)
fi

WRK_ID=$(head -1 "$ACTIVE_WRK_FILE" | tr -d '[:space:]')
if [[ -z "$WRK_ID" || "$WRK_ID" == *"started_at"* ]]; then
    # active-wrk may have multi-line format; extract just the ID
    WRK_ID=$(grep -oP 'WRK-\d+' "$ACTIVE_WRK_FILE" | head -1)
fi

if [[ -z "$WRK_ID" ]]; then
    exit 0  # Can't determine WRK — allow
fi

# Check for stage-timing evidence
TIMING_DIR="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence"
if [[ ! -d "$TIMING_DIR" ]]; then
    echo "BLOCKED: No evidence directory for $WRK_ID. Run start_stage.py before committing." >&2
    exit 2
fi

TIMING_COUNT=$(find "$TIMING_DIR" -name "stage-timing-*.yaml" 2>/dev/null | wc -l)
if [[ "$TIMING_COUNT" -eq 0 ]]; then
    echo "BLOCKED: No stage-timing files for $WRK_ID. Agent must use start_stage.py/exit_stage.py — not bypass stage machinery." >&2
    exit 2
fi

exit 0
