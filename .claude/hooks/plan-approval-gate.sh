#!/usr/bin/env bash
# plan-approval-gate.sh - PreToolUse hook enforcing plan-approval hard-stop
# Issue: #1839 - Block implementation writes when no approved plan marker exists
#
# Convention: After the user approves a plan, the agent writes a marker file:
#   .planning/plan-approved/<issue-number>.md
#   OR  .planning/plan-approved/session.md
#
# Protocol: stdout JSON for Claude context, stderr for user terminal.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
WS="${WORKSPACE_HUB:-$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
APPROVAL_DIR="$WS/.planning/plan-approved"

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)

if [[ "${SKIP_PLAN_APPROVAL_GATE:-}" == "1" ]]; then
  echo "[plan-gate] SKIP: Plan approval gate bypassed." >&2
  exit 0
fi

has_approval() {
  if [[ -d "$APPROVAL_DIR" ]]; then
    local found
    found=$(find "$APPROVAL_DIR" -name '*.md' -type f 2>/dev/null | head -1)
    [[ -n "$found" ]]
  else
    return 1
  fi
}

is_safe_path() {
  local p="$1"
  local rel="${p##*/}"
  case "$p" in
    */.planning/*|*/docs/plans/*|*/docs/governance/*|*/docs/reports/*|*/docs/standards/*) return 0 ;;
    */tests/*|*/.claude/*|*/scripts/workflow/*|*/scripts/enforcement/*) return 0 ;;
    */docs/handoffs/*|*/notes/*|*/knowledge/*) return 0 ;;
  esac
  case "$rel" in
    CLAUDE.md|AGENTS.md|MEMORY.md|GEMINI.md) return 0 ;;
  esac
  case "$p" in
    *.md) return 0 ;;
  esac
  return 1
}

if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "MultiEdit" ]]; then
  [[ -z "$FILE_PATH" ]] && exit 0
  is_safe_path "$FILE_PATH" && exit 0
  has_approval && exit 0

  echo "[plan-gate] BLOCKED: No plan-approval marker found." >&2
  echo "[plan-gate] Create: .planning/plan-approved/<issue>.md after user approves plan." >&2
  printf '{"decision":"block","reason":"Plan approval required before implementation. No marker in .planning/plan-approved/. Safe paths (.planning/, docs/, tests/, .claude/) are not blocked."}\n'
  exit 0
fi

if [[ "$TOOL_NAME" == "Bash" && -n "$COMMAND" ]]; then
  if echo "$COMMAND" | grep -qE 'git\s+push'; then
    has_approval && exit 0
    echo "[plan-gate] BLOCKED: git push requires plan approval." >&2
    printf '{"decision":"block","reason":"Plan approval required before pushing. No marker in .planning/plan-approved/."}\n'
    exit 0
  fi
fi

exit 0
