#!/usr/bin/env bash
# WRK-1316 L3 Hook: Block Bash writes to evidence directories
#
# Prevents: cat > evidence/foo.yaml, echo > evidence/bar.yaml, etc.
# Evidence files MUST be written via Write tool (not Bash redirects).
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)

# Block backfill-stage-evidence.py — maintenance tool, not for active processing
# Only match when it's actually being executed (not just mentioned in a commit message)
if echo "$COMMAND" | grep -qP '(python|bash|uv run).*backfill-stage-evidence' 2>/dev/null; then
    echo "BLOCKED: backfill-stage-evidence.py is a maintenance tool, not for active WRK processing." >&2
    echo "  Use start_stage.py and exit_stage.py to manage stage evidence." >&2
    exit 2
fi

# Block Bash commands that write to stage-evidence.yaml (not just mention it)
# Allow: cat, grep, read, ls (read-only); block: >, >>, cp, mv, echo > (write)
if echo "$COMMAND" | grep -qP '(>|cp|mv)\s*.*stage-evidence\.yaml' 2>/dev/null; then
    echo "BLOCKED: stage-evidence.yaml is managed by start_stage.py/exit_stage.py only." >&2
    exit 2
fi

# Only check Bash commands that write to evidence paths
if [[ "$COMMAND" != *"evidence/"* ]]; then
    exit 0
fi

# Check for redirect/write patterns targeting evidence directories
# Block: cat >, echo >, tee, >> to evidence paths
if echo "$COMMAND" | grep -qP '(cat|echo|printf|tee)\s.*>.*evidence/' 2>/dev/null; then
    echo "BLOCKED: Use Write tool (not Bash cat/echo) for evidence files. Rule: stage micro-skills." >&2
    exit 2
fi

# Block: heredoc writes to evidence paths
if echo "$COMMAND" | grep -qP "cat\s*<<.*evidence/" 2>/dev/null; then
    echo "BLOCKED: Use Write tool (not Bash heredoc) for evidence files." >&2
    exit 2
fi

# Block: cp to evidence paths (agent copies from /tmp to bypass)
if echo "$COMMAND" | grep -qP '(cp|mv)\s.*evidence/' 2>/dev/null; then
    echo "BLOCKED: Use Write tool (not cp/mv) for evidence files." >&2
    exit 2
fi

exit 0
