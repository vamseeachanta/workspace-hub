#!/usr/bin/env bash
# Refresh ace-win-2 curation/equality evidence and optionally push the generated commit.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

MACHINE="${RECONCILE_MACHINE:-ace-win-2}"
APPLY=0
PUSH=0

usage() {
  cat <<'EOF'
Usage: bash scripts/readiness/gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh [--apply] [--push]

Default mode is read-only: print current gaps only.

Options:
  --apply   Run curation and equality report refresh for ace-win-2
  --push    After --apply, commit generated changes and push main
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --push) PUSH=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ $APPLY -eq 0 ]]; then
  bash scripts/readiness/gap-actions/ace-win-2/00-current-gaps.sh "$MACHINE"
  exit 0
fi

case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) ;;
  *) echo "Run --apply from Git Bash on Windows." >&2; exit 2 ;;
esac

command -v powershell.exe >/dev/null 2>&1 || { echo "powershell.exe is required." >&2; exit 1; }

powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/curation/curate-session-memory.ps1 -Machine "$MACHINE"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/windows/equality-report.ps1 -Machine "$MACHINE" -RefreshMatrix

bash scripts/readiness/gap-actions/ace-win-2/00-current-gaps.sh "$MACHINE"

if [[ $PUSH -eq 1 ]]; then
  publish_paths=(
    ".claude/state/equality-${MACHINE}.yaml"
    ".claude/state/session-curation-${MACHINE}.json"
    ".claude/state/session-curation-digest-${MACHINE}.md"
    ".claude/state/memory-freshness-${MACHINE}.json"
    ".claude/state/skill-currency-${MACHINE}.json"
    ".claude/state/skill-drift-${MACHINE}.json"
    ".claude/state/skill-drift-report-${MACHINE}.json"
    ".claude/state/skill-link-health-${MACHINE}.json"
    "docs/reports/machine-equality-matrix.html"
  )
  for report in docs/reports/*machine-equality-matrix.html; do
    [[ -e "$report" ]] && publish_paths+=("$report")
  done
  existing=()
  for path in "${publish_paths[@]}"; do
    [[ -e "$path" ]] && existing+=("$path")
  done
  git add -- "${existing[@]}"
  if git diff --cached --quiet; then
    echo "No generated changes to commit."
  else
    git commit -m "chore(equality): refresh ${MACHINE} evidence" -- "${existing[@]}"
    git push
  fi
fi
