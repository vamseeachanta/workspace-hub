#!/usr/bin/env bash
# Read-only preflight for the ace-win-2 Hermes harness/memory divergence rows.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

home_dir="${HOME:-}"
[[ -n "$home_dir" ]] || { echo "HOME is not set." >&2; exit 1; }

echo "Hermes executable:"
if command -v hermes >/dev/null 2>&1; then
  command -v hermes
else
  echo "missing"
fi

echo
echo "Required surfaces:"
paths=(
  "config/agents/hermes/SOUL.runtime.md"
  "$home_dir/.hermes/SOUL.md"
  "$home_dir/.hermes/config.yaml"
  "$home_dir/.hermes/memories"
)

missing=0
for path in "${paths[@]}"; do
  if [[ -e "$path" ]]; then
    echo "present: $path"
  else
    echo "missing: $path"
    missing=1
  fi
done

echo
if [[ -f "$home_dir/.hermes/config.yaml" ]]; then
  if grep -F '.claude/skills' "$home_dir/.hermes/config.yaml" >/dev/null 2>&1; then
    echo "Hermes skills config references repo .claude/skills."
  else
    echo "Hermes skills config does not reference repo .claude/skills."
    missing=1
  fi
fi

if [[ -f "$home_dir/.hermes/SOUL.md" ]]; then
  if grep -E 'Plan ALL issues|TDD mandatory|USER APPROVES' "$home_dir/.hermes/SOUL.md" >/dev/null 2>&1; then
    echo "Hermes SOUL.md contains workflow gate text."
  else
    echo "Hermes SOUL.md is missing expected workflow gate text."
    missing=1
  fi
fi

if [[ $missing -ne 0 ]]; then
  echo
  echo "Hermes gap remains. This script is read-only because Hermes config is local runtime state."
  echo "After fixing the missing surfaces, run:"
  echo "  bash scripts/readiness/gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh --apply --push"
  exit 2
fi

echo
echo "Hermes local surfaces look complete. Refresh equality evidence next."
