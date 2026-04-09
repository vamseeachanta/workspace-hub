#!/usr/bin/env bash
# post-commit-learnings.sh — Post-commit learning extraction pipeline hook
# Issue: #2027
#
# Runs after each commit to:
# 1. Track skill modifications (existing #1719 pipeline)
# 2. Extract learnings from the commit (extract-learnings.sh)
#
# Wire into .git/hooks/post-commit by adding (BEFORE exit 0):
#   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
#   bash "${REPO_ROOT}/scripts/hooks/post-commit-learnings.sh" || true
#
# Or run standalone:
#   bash scripts/hooks/post-commit-learnings.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Track skill modifications for learning pipeline (#1719)
if [[ -f "${REPO_ROOT}/scripts/hooks/track-skill-patches.sh" ]]; then
  bash "${REPO_ROOT}/scripts/hooks/track-skill-patches.sh" 2>/dev/null || true
fi

# Extract learnings from commit (#2027)
if [[ -f "${REPO_ROOT}/scripts/learnings/extract-learnings.sh" ]]; then
  bash "${REPO_ROOT}/scripts/learnings/extract-learnings.sh" HEAD > /tmp/post-commit-learnings.log 2>&1 || true
fi
