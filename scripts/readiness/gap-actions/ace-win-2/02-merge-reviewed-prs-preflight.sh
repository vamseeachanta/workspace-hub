#!/usr/bin/env bash
# Check whether the reviewed ace-win-2 blocker PRs are mergeable; optionally merge only if green.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

MERGE=0
PRS=(3540 3563)

usage() {
  cat <<'EOF'
Usage: bash scripts/readiness/gap-actions/ace-win-2/02-merge-reviewed-prs-preflight.sh [--merge]

Checks:
  #3540 - Windows equivalence sentinel hardening (#3511)
  #3563 - Windows-portable equality publisher (#3554)

Without --merge this is read-only. With --merge it still refuses unless all checks are green.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --merge) MERGE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "gh is required." >&2; exit 1; }

blocked=0
for pr in "${PRS[@]}"; do
  echo "== PR #$pr =="
  state="$(gh pr view "$pr" --json state --jq .state)"
  merge_state="$(gh pr view "$pr" --json mergeStateStatus --jq .mergeStateStatus)"
  echo "state=$state mergeStateStatus=$merge_state"

  if [[ "$state" != "OPEN" ]]; then
    echo "blocked: PR is not open"
    blocked=1
    continue
  fi

  failures="$(gh pr checks "$pr" --json name,state,link 2>/dev/null \
    --jq '.[] | select(.state != "SUCCESS" and .state != "SKIPPED" and .state != "NEUTRAL") | "- \(.name): \(.state) \(.link)"' || true)"
  if [[ -n "$failures" ]]; then
    echo "blocked checks:"
    printf '%s\n' "$failures"
    blocked=1
  else
    echo "checks: green"
  fi
done

if [[ $blocked -ne 0 ]]; then
  echo
  echo "Merge blocked. Resolve the listed checks before using --merge."
  exit 2
fi

if [[ $MERGE -eq 1 ]]; then
  for pr in "${PRS[@]}"; do
    gh pr merge "$pr" --squash --delete-branch
  done
else
  echo
  echo "Preflight green. Re-run with --merge to merge these PRs."
fi
