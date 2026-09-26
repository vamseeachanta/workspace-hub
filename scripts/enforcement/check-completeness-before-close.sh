#!/usr/bin/env bash
# check-completeness-before-close.sh — #2798
#
# ADVISORY local pre-flight (NOT the authoritative gate — that is the
# `.github/workflows/completeness-gate.yml` Action on issues.closed, because a
# local hook cannot intercept the `gh issue close` REST call).
#
# Gives fast local feedback before you attempt to close an issue: does it carry
# a valid computed completeness record + owner verified label that would pass the
# server-side gate?
#
# Usage:
#   scripts/enforcement/check-completeness-before-close.sh <issue-number>
#
# Bypass: COMPLETENESS_ALLOW=1 (logged to stderr). Use sparingly.
# Config:  COMPLETENESS_OWNERS=comma,separated,logins  CLOSING_ACTOR=<you>
set -euo pipefail

issue="${1:-}"
if [[ -z "$issue" ]]; then
  echo "usage: $0 <issue-number>" >&2
  exit 2
fi

if [[ "${COMPLETENESS_ALLOW:-0}" == "1" ]]; then
  echo "check-completeness-before-close: BYPASSED via COMPLETENESS_ALLOW=1 (issue #$issue)" >&2
  exit 0
fi

repo_root="$(git rev-parse --show-toplevel)"
: "${REPO:=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo '')}"
export REPO ISSUE_NUMBER="$issue"
export CLOSING_ACTOR="${CLOSING_ACTOR:-$(gh api user -q .login 2>/dev/null || echo '')}"

if python3 "$repo_root/scripts/workflow/completeness_gate_runner.py" "$issue"; then
  echo "check-completeness-before-close: PASS (issue #$issue would close cleanly)" >&2
  exit 0
else
  echo "check-completeness-before-close: FAIL — the server-side gate would reopen issue #$issue (see message above)" >&2
  exit 1
fi
