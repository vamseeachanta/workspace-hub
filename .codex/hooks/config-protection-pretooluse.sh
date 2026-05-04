#!/usr/bin/env bash
# config-protection-pretooluse.sh — Claude Code PreToolUse hook for protected config edits
# Blocks risky weakening of lint/formatter configs and removal of core safety gates
# from CLAUDE.md / AGENTS.md unless CONFIG_PROTECTION_APPROVED=1 is set.

set -euo pipefail

REPO_ROOT="${REPO_ROOT_OVERRIDE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
CHECKER="${REPO_ROOT}/scripts/enforcement/check-config-protection.sh"

INPUT="$(cat)"
if [[ ! -x "$CHECKER" ]]; then
  # Run via bash even if executable bit is missing.
  true
fi

RESULT="$(printf '%s' "$INPUT" | bash "$CHECKER" 2>/dev/null)" || exit 0

if [[ -n "$RESULT" ]]; then
  printf '%s\n' "$RESULT"
fi

exit 0
