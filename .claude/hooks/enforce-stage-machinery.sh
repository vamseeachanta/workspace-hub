#!/usr/bin/env bash
# WRK-1316 L3 Hook: Enforce stage machinery for evidence writes
#
# Blocks Write/Edit to evidence/ directories unless start_stage.py has been
# called (stage-evidence.yaml shows a stage in_progress).
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

# Read tool input from stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)

# Only check writes to evidence directories
if [[ "$FILE_PATH" != *"/evidence/"* ]]; then
    exit 0
fi

# Extract WRK ID from path (e.g., .../assets/WRK-1316/evidence/foo.yaml)
WRK_ID=$(echo "$FILE_PATH" | grep -oP 'WRK-\d+' | head -1)
if [[ -z "$WRK_ID" ]]; then
    exit 0  # Not a WRK evidence path — allow
fi

# Check if stage-evidence.yaml exists with an in_progress stage
STAGE_EV="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence/stage-evidence.yaml"
if [[ ! -f "$STAGE_EV" ]]; then
    echo "BLOCKED: No stage-evidence.yaml for $WRK_ID. Run start_stage.py first." >&2
    exit 2
fi

# Check for in_progress status
if ! grep -q "in_progress" "$STAGE_EV" 2>/dev/null; then
    echo "BLOCKED: No stage in_progress for $WRK_ID. Run start_stage.py before writing evidence." >&2
    exit 2
fi

exit 0
