#!/usr/bin/env bash
# WRK-1316 L3 Hook: Block all work unless a stage is in_progress
#
# If an active WRK exists but no stage is in_progress, block everything
# except start_stage.py calls, Read, Glob, Grep (read-only exploration ok).
#
# This forces the agent to call start_stage.py before doing ANY work.
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

# Read tool input from stdin
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)

# Always allow read-only tools — agent needs to explore before starting
case "$TOOL_NAME" in
    Read|Glob|Grep|LS|WebSearch|WebFetch|Agent|TaskCreate|TaskGet|TaskList|TaskOutput|TaskStop|TaskUpdate|SendMessage|Skill|EnterPlanMode|ExitPlanMode|AskUserQuestion|ToolSearch)
        exit 0
        ;;
esac

# Always allow stage machinery scripts and queue management
if echo "$COMMAND" | grep -qP '(start_stage\.py|exit_stage\.py|set-active-wrk\.sh|clear-active-wrk\.sh|work\.sh|session\.sh|next-id\.sh|validate-wrk-frontmatter|claim-item\.sh|close-item\.sh|archive-item\.sh|generate-html-review|verify-gate-evidence|is-human-gate|checkpoint|queue-status|whats-next|cross-review)' 2>/dev/null; then
    exit 0
fi

# Always allow git status/log/diff (read-only git ops)
if echo "$COMMAND" | grep -qP '^\s*git\s+(status|log|diff|show|branch|rev-parse|fetch)' 2>/dev/null; then
    exit 0
fi

# Always allow filesystem ops and read-only shell commands
if echo "$COMMAND" | grep -qP '^\s*(mkdir|rm|ls|find|cat|head|tail|wc|grep|rg|echo|chmod|cp|mv|touch|stat|file|diff|date|hostname|which|pwd|tree|du|df|sort|uniq|cut|tr|awk|sed|jq|yq|xargs|tee)\b' 2>/dev/null; then
    exit 0
fi

# Always allow uv run pytest (testing is always ok)
if echo "$COMMAND" | grep -qP 'pytest' 2>/dev/null; then
    exit 0
fi

# Check for active WRK
ACTIVE_WRK_FILE="$REPO_ROOT/.claude/state/active-wrk"
if [[ ! -f "$ACTIVE_WRK_FILE" ]]; then
    exit 0  # No active WRK — not in a WRK workflow, allow everything
fi

WRK_ID=$(grep -oP 'WRK-\d+' "$ACTIVE_WRK_FILE" 2>/dev/null | head -1)
if [[ -z "$WRK_ID" ]]; then
    exit 0  # Can't determine WRK — allow
fi

# Check if a stage is in_progress
STAGE_EV="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence/stage-evidence.yaml"
if [[ ! -f "$STAGE_EV" ]]; then
    echo "BLOCKED: Active WRK $WRK_ID has no stage-evidence.yaml." >&2
    echo "  Run: uv run --no-project python scripts/work-queue/start_stage.py $WRK_ID 1" >&2
    exit 2
fi

if grep -q "in_progress" "$STAGE_EV" 2>/dev/null; then
    exit 0  # A stage is in_progress — allow work
fi

# All stages are done or pending — no active stage
echo "BLOCKED: Active WRK $WRK_ID has no stage in_progress." >&2
echo "  Run start_stage.py for the next stage before doing work." >&2
exit 2
