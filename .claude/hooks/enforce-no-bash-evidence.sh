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

exit 0
