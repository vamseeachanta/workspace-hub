#!/usr/bin/env bash
# stage-prompt-drift-status.sh — Local doctor/status for the stage-prompt drift guard.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PRE_PUSH_HOOK="${REPO_ROOT}/.git/hooks/pre-push"
GUARD_SCRIPT="${REPO_ROOT}/scripts/enforcement/require-stage-prompt-drift.sh"
HOOK_REFERENCE="require-stage-prompt-drift.sh"

status_word() {
  if [[ "$1" == "1" ]]; then
    printf 'yes'
  else
    printf 'no'
  fi
}

script_exists=0
pre_push_exists=0
hook_references_guard=0

if [[ -f "$GUARD_SCRIPT" ]]; then
  script_exists=1
fi

if [[ -f "$PRE_PUSH_HOOK" ]]; then
  pre_push_exists=1
  if grep -Fq "$HOOK_REFERENCE" "$PRE_PUSH_HOOK"; then
    hook_references_guard=1
  fi
fi

overall_status="INACTIVE"
exit_code=1
if [[ "$script_exists" == "1" && "$pre_push_exists" == "1" && "$hook_references_guard" == "1" ]]; then
  overall_status="ACTIVE"
  exit_code=0
fi

printf 'stage-prompt-drift guard status: %s\n' "$overall_status"
printf '  guard script present: %s (%s)\n' "$(status_word "$script_exists")" "$GUARD_SCRIPT"
printf '  pre-push hook present: %s (%s)\n' "$(status_word "$pre_push_exists")" "$PRE_PUSH_HOOK"
printf '  pre-push references guard: %s\n' "$(status_word "$hook_references_guard")"

if [[ "$exit_code" -ne 0 ]]; then
  printf 'remediation: run bash scripts/enforcement/install-hooks.sh\n'
fi

exit "$exit_code"
