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
    local markers
    markers=$(find "$APPROVAL_DIR" -name '*.md' -type f 2>/dev/null)
    [[ -z "$markers" ]] && return 1
    # Check each marker — accept if ANY one is legitimate (#2047)
    while IFS= read -r marker; do
      [[ -z "$marker" ]] && continue
      if ! is_self_approved "$marker"; then
        return 0  # found a legitimate (non-self-approved) marker
      fi
    done <<< "$markers"
    # All markers were self-approved
    echo "[plan-gate] WARN: All approval markers appear self-created." >&2
    return 1
  else
    return 1
  fi
}

is_self_approved() {
  local marker="$1"
  # Check 1: marker contains "Worker session" or "Authority: Worker" (auto-created)
  if grep -qiE '(Worker session|auto-approved|self-approved)' "$marker" 2>/dev/null; then
    return 0  # is self-approved
  fi
  # Check 2: marker was created very recently (within 120s) AND is in git staging
  # This catches the pattern where an agent creates a marker then immediately writes code
  local marker_age_s
  marker_age_s=$(( $(date +%s) - $(stat -c %Y "$marker" 2>/dev/null || echo 0) ))
  if [[ "$marker_age_s" -lt 120 ]]; then
    if git -C "$WS" rev-parse --git-dir &>/dev/null 2>&1; then
      local rel_path="${marker#"$WS"/}"
      if ! git -C "$WS" log --oneline -1 -- "$rel_path" 2>/dev/null | grep -q .; then
        return 0  # is self-approved (new file, never committed in this git repo)
      fi
    fi
  fi
  return 1  # not self-approved
}

is_safe_path() {
  local p="$1"
  local rel="${p##*/}"
  # Planning artifacts, governance docs, and harness infrastructure — always allowed
  case "$p" in
    */.planning/*|*/docs/plans/*|*/docs/governance/*|*/docs/reports/*|*/docs/standards/*) return 0 ;;
    */docs/handoffs/*|*/notes/*) return 0 ;;
    */.claude/*|*/.git/hooks/*) return 0 ;;
    */scripts/workflow/*|*/scripts/enforcement/*) return 0 ;;
    */tests/*|*/test_*) return 0 ;;
  esac
  # Harness config files and standard root documentation — always allowed
  case "$rel" in
    CLAUDE.md|AGENTS.md|MEMORY.md|GEMINI.md|README.md|CHANGELOG.md|LICENSE) return 0 ;;
  esac
  # NOTE: *.md catch-all REMOVED (#2047) — was allowing all implementation to bypass gate
  # NOTE: scripts/ (general), knowledge/* REMOVED (#2047) — too broad
  # NOTE: tests/* RESTORED — TDD requires test writes before plan approval (#2056)
  return 1
}

if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "MultiEdit" ]]; then
  [[ -z "$FILE_PATH" ]] && exit 0
  is_safe_path "$FILE_PATH" && exit 0
  has_approval && exit 0

  echo "[plan-gate] BLOCKED: No plan-approval marker found." >&2
  echo "[plan-gate] Create: .planning/plan-approved/<issue>.md after user approves plan." >&2
  printf '{"decision":"block","reason":"Plan approval required before implementation. No marker in .planning/plan-approved/. Safe paths: .planning/, docs/plans/, docs/governance/, .claude/, scripts/enforcement/."}\n'
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
