#!/usr/bin/env bash
# check-config-protection.sh — detect risky weakening of protected config and guard docs
# Usage:
#   bash scripts/enforcement/check-config-protection.sh <file_path>
# Reads JSON payload on stdin with Claude Code PreToolUse structure.

set -euo pipefail

INPUT="$(cat)"
FILE_PATH="${1:-}"

if [[ -z "$FILE_PATH" ]]; then
  FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
fi

TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)"
OLD_STRING="$(echo "$INPUT" | jq -r '.tool_input.old_string // ""' 2>/dev/null || true)"
NEW_STRING="$(echo "$INPUT" | jq -r '.tool_input.new_string // .tool_input.content // ""' 2>/dev/null || true)"
BASENAME="$(basename "$FILE_PATH")"
COMBINED="${OLD_STRING}
${NEW_STRING}"
LOWER_COMBINED="$(printf '%s' "$COMBINED" | tr '[:upper:]' '[:lower:]')"
LOWER_OLD="$(printf '%s' "$OLD_STRING" | tr '[:upper:]' '[:lower:]')"
LOWER_NEW="$(printf '%s' "$NEW_STRING" | tr '[:upper:]' '[:lower:]')"

if [[ "${CONFIG_PROTECTION_APPROVED:-0}" == "1" ]]; then
  exit 0
fi

if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "MultiEdit" ]]; then
  exit 0
fi

is_protected=0
case "$BASENAME" in
  pyproject.toml|setup.cfg|.flake8|.ruff.toml|ruff.toml|.eslintrc|.eslintrc.json|.eslintrc.js|.eslintrc.cjs|.prettierrc|.prettierrc.json|package.json|CLAUDE.md|AGENTS.md)
    is_protected=1
    ;;
esac

if [[ $is_protected -eq 0 ]]; then
  exit 0
fi

block() {
  local reason="$1"
  printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | jq -Rs .)"
  exit 0
}

# Allowlist: metadata edits in pyproject.toml outside tooling sections are okay.
if [[ "$BASENAME" == "pyproject.toml" ]]; then
  if ! printf '%s' "$LOWER_COMBINED" | grep -Eq 'tool\.(ruff|black|mypy|pytest|coverage)|\[tool\.'; then
    exit 0
  fi
fi

# Allowlist: dependency-only edits in package.json outside eslint/prettier config are okay.
if [[ "$BASENAME" == "package.json" ]]; then
  if ! printf '%s' "$LOWER_COMBINED" | grep -Eq 'eslint|prettier'; then
    exit 0
  fi
fi

# Guard docs: don't allow removal of core safety gates.
if [[ "$BASENAME" == "CLAUDE.md" || "$BASENAME" == "AGENTS.md" ]]; then
  required_phrases=(
    "Plan before acting|plan before acting"
    "TDD mandatory|tdd mandatory"
    "Cross-review|cross-review"
    "Secrets: never hardcode|secrets: never hardcode"
  )
  removed=()
  for phrase_pair in "${required_phrases[@]}"; do
    display_label="${phrase_pair%%|*}"
    phrase="${phrase_pair##*|}"
    if printf '%s' "$LOWER_OLD" | grep -Fq "$phrase" && ! printf '%s' "$LOWER_NEW" | grep -Fq "$phrase"; then
      removed+=("$display_label")
    fi
  done
  if [[ ${#removed[@]} -gt 0 ]]; then
    block "Config protection blocked a safety-gate removal in ${BASENAME}. Missing in replacement text: ${removed[*]}. Set CONFIG_PROTECTION_APPROVED=1 only for explicitly approved governance changes."
  fi
  exit 0
fi

# Direct lint/formatter config files: block broad weakening patterns.
if printf '%s' "$LOWER_NEW" | grep -Eq '(^|[^a-z])(ignore|extend-ignore|per-file-ignores|noqa|disable|skip|off)([^a-z]|$)'; then
  block "Config protection blocked a potentially weakening change to ${BASENAME}. Broad ignore/disable patterns require explicit approval. Set CONFIG_PROTECTION_APPROVED=1 if this config change is intentional and user-approved."
fi

# pyproject/setup.cfg/package.json tool config weakening patterns
if printf '%s' "$LOWER_COMBINED" | grep -Eq 'tool\.(ruff|black|mypy|pytest)|eslint|prettier|flake8'; then
  if printf '%s' "$LOWER_NEW" | grep -Eq '(^|[^a-z])(ignore|extend-ignore|per-file-ignores|noqa|disable|skip|off)([^a-z]|$)'; then
    block "Config protection blocked a potentially weakening tooling change in ${BASENAME}. Ignore/disable patterns in lint or formatter config require explicit approval."
  fi
fi

exit 0
