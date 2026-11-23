#!/usr/bin/env bash
# post-commit-learning.sh — Extract learnings after every commit
# Phase 4 of #1760: Auto-generate issues from patterns, update skills
# 
# Install: Copy to .git/hooks/post-commit-learnings (then chain from post-commit)
# Or run standalone: bash scripts/learnings/extract-learnings.sh HEAD
#
# Guards: Same auto-push guards; lightweight; < 5 seconds

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Skip in batch/cron contexts
[[ -n "${CI:-}" || -n "${GITHUB_ACTIONS:-}" ]] && exit 0

# Skip if no learning extraction configured
EXTRACT_SCRIPT="${REPO_ROOT}/scripts/learnings/extract-learnings.sh"
if [[ -f "$EXTRACT_SCRIPT" ]]; then
  # Run in background so it doesn't slow down the commit
  (bash "$EXTRACT_SCRIPT" HEAD >> "${REPO_ROOT}/logs/learnings/extraction.log" 2>&1) &
fi
