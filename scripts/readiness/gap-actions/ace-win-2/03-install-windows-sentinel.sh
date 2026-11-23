#!/usr/bin/env bash
# Install the Windows equivalence scheduler tasks after #3511 is present on main.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

MACHINE="${RECONCILE_MACHINE:-ace-win-2}"
APPLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    -h|--help)
      echo "Usage: bash $0 [--apply]"
      exit 0
      ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) ;;
  *) echo "Run this from Git Bash on Windows." >&2; exit 2 ;;
esac

required=(
  scripts/windows/equivalence-sentinel.ps1
  scripts/windows/scheduler-yaml.ps1
  scripts/windows/setup-scheduler-tasks.ps1
)
missing=0
for path in "${required[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "missing: $path"
    missing=1
  fi
done

if [[ $missing -ne 0 ]]; then
  echo "blocked: merge PR #3540 / issue #3511 before installing the sentinel tasks."
  exit 2
fi

if [[ $APPLY -eq 0 ]]; then
  echo "Ready. Re-run with --apply to install scheduler tasks for $MACHINE."
  echo "Preview command: bash scripts/windows/schedule-equivalence-tasks.sh --machine $MACHINE --what-if"
  bash scripts/windows/schedule-equivalence-tasks.sh --machine "$MACHINE" --what-if
  exit 0
fi

bash scripts/windows/schedule-equivalence-tasks.sh --machine "$MACHINE"
