#!/usr/bin/env bash
# audit-pending-status.sh — Find pending/ items with status that doesn't match directory
# Usage: bash scripts/work-queue/audit-pending-status.sh [--fix]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="${REPO_ROOT}/.claude/work-queue"
FIX=false
[[ "${1:-}" == "--fix" ]] && FIX=true

misplaced=0
for f in "${QUEUE_DIR}/pending"/WRK-*.md; do
  [[ -f "$f" ]] || continue
  status=$(grep -m1 '^status:' "$f" 2>/dev/null | sed 's/^status: *//' | tr -d '"' || echo "")
  case "$status" in
    closed|done|archived)
      wrk_id=$(basename "$f" .md)
      echo "MISPLACED: $wrk_id (status: $status) in pending/"
      if $FIX; then
        target_dir="${QUEUE_DIR}/done"
        [[ "$status" == "archived" ]] && target_dir="${QUEUE_DIR}/archive/$(date +%Y-%m)"
        mkdir -p "$target_dir"
        git mv "$f" "$target_dir/" 2>/dev/null || mv "$f" "$target_dir/"
        echo "  → moved to $target_dir/"
      fi
      misplaced=$((misplaced + 1))
      ;;
  esac
done

if [[ $misplaced -eq 0 ]]; then
  echo "✔ No misplaced items in pending/"
else
  echo "Found $misplaced misplaced item(s)"
  $FIX || echo "Run with --fix to relocate them"
fi
