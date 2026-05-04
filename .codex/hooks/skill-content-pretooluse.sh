#!/usr/bin/env bash
# skill-content-pretooluse.sh — Claude Code PreToolUse hook for skill content scanning
# Reads tool_input from stdin (JSON), checks if a Read tool is loading a skill file,
# and runs check-skill-content.sh against it to block malicious content injection.
#
# Wired as a PreToolUse hook in .claude/settings.json for the Read tool.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCANNER="${REPO_ROOT}/.claude/hooks/check-skill-content.sh"

# Read stdin (JSON from Claude Code hook system)
INPUT="$(cat)"

# Extract the tool name
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null || true)"

# Only intercept Read operations
if [[ "$TOOL_NAME" != "Read" ]]; then
  exit 0
fi

# Extract file_path from tool_input
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null || true)"

# Only scan skill files
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Match skill file paths (both relative and absolute)
IS_SKILL=0
case "$FILE_PATH" in
  *.claude/skills/*.md)  IS_SKILL=1 ;;
  */.claude/skills/*.md) IS_SKILL=1 ;;
esac

if [[ $IS_SKILL -eq 0 ]]; then
  exit 0
fi

# File must exist
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# Run the scanner in direct mode
SCAN_OUTPUT="$(bash "$SCANNER" --scan-file "$FILE_PATH" 2>&1)" || {
  # Scanner found threats — emit advisory warning via hook output
  # Note: we emit as advisory (exit 0 with context) rather than blocking,
  # because Read is used broadly and we don't want false-positive deadlocks.
  ESCAPED_OUTPUT="$(echo "$SCAN_OUTPUT" | head -20 | jq -Rs '.' 2>/dev/null || echo '"scan output unavailable"')"
  cat <<ENDJSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "SECURITY WARNING: Skill file ${FILE_PATH} contains potential threats. Scanner output: ${SCAN_OUTPUT}"
  }
}
ENDJSON
  exit 0
}

# Clean — no output needed
exit 0
