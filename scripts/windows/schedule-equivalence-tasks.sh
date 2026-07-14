#!/usr/bin/env bash
# Install the Windows machine-equivalence Task Scheduler jobs from Git Bash.
# The canonical schedules and task definitions remain in schedule-tasks.yaml and
# setup-scheduler-tasks.ps1; this is only a convenient shell entry point.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MACHINE="${RECONCILE_MACHINE:-}"
MACHINE_EXPLICIT=0
WHAT_IF=0

usage() {
  cat <<'EOF'
Usage: bash scripts/windows/schedule-equivalence-tasks.sh [options]

Options:
  --machine ace-win-1|ace-win-2  WhatIf-only public fleet identity
  --what-if                      Preview without changing Task Scheduler
  -h, --help                     Show this help

Installs only:
  EcosystemReconcile  daily 05:15, report-only
  SessionCuration     every 6 hours at minute 47
  EqualityReport      Monday 04:30
  EquivalenceSentinel every 6 hours at minute 17
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --machine)
      [[ $# -ge 2 ]] || { echo "--machine requires a value" >&2; exit 2; }
      MACHINE="$2"
      MACHINE_EXPLICIT=1
      shift 2
      ;;
    --what-if) WHAT_IF=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ $WHAT_IF -eq 1 ]]; then
  case "$MACHINE" in
    ace-win-1|ace-win-2) ;;
    *) echo "WhatIf requires --machine ace-win-1|ace-win-2 (or RECONCILE_MACHINE)." >&2; exit 2 ;;
  esac
elif [[ $MACHINE_EXPLICIT -eq 1 ]]; then
  echo "--machine is allowed only with --what-if; live installs use physical host identity." >&2
  exit 2
fi

case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) ;;
  *) echo "Run this wrapper from Git Bash on Windows." >&2; exit 2 ;;
esac

command -v powershell.exe >/dev/null 2>&1 || {
  echo "powershell.exe is required." >&2
  exit 1
}
command -v cygpath >/dev/null 2>&1 || {
  echo "cygpath is required (provided by Git for Windows)." >&2
  exit 1
}

installer="$(cygpath -w "$REPO_ROOT/scripts/windows/setup-scheduler-tasks.ps1")"
workspace="$(cygpath -w "$REPO_ROOT")"
args=(-NoProfile -ExecutionPolicy Bypass -File "$installer" -WorkspaceRoot "$workspace" -EquivalenceOnly)
[[ $WHAT_IF -eq 1 ]] && args+=(-WhatIf -MachineIdOverride "$MACHINE")

powershell.exe "${args[@]}"

if [[ $WHAT_IF -eq 0 ]]; then
  echo
  echo "Installed machine-equivalence tasks for the physical Windows host."
  echo "Verify: powershell.exe -NoProfile -Command \"Get-ScheduledTask -TaskPath '\\Claude\\'\""
fi
