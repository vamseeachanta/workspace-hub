#!/usr/bin/env bash
# Run the equivalence sentinel and refresh publish-health evidence after #3511/#3554 land.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

MACHINE="${RECONCILE_MACHINE:-ace-win-2}"

required=(
  scripts/windows/equivalence-sentinel.ps1
  scripts/monitoring/equivalence_schema.py
)
missing=0
for path in "${required[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "missing: $path"
    missing=1
  fi
done
if [[ $missing -ne 0 ]]; then
  echo "blocked: merge PR #3540 / issue #3511 before running the hardened sentinel."
  exit 2
fi

if grep -q 'flock -n' scripts/readiness/publish-equality.sh; then
  echo "blocked: scripts/readiness/publish-equality.sh still depends on flock."
  echo "merge PR #3563 / issue #3554 first."
  exit 2
fi

bash scripts/monitoring/equivalence-sentinel.sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/windows/equality-report.ps1 -Machine "$MACHINE" -RefreshMatrix

bash scripts/readiness/gap-actions/ace-win-2/00-current-gaps.sh "$MACHINE"
