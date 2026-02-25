#!/usr/bin/env bash
# ABOUTME: Daily log section — branch status (current, recent, stale)
# Usage: bash branch-status.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$WORKSPACE_ROOT"

echo "### Branch Status"
echo ""
echo "**Current branch:** $(git branch --show-current 2>/dev/null)"
echo ""
echo "**Recent branches:**"
git branch --sort=-committerdate | head -5 | while read -r branch; do echo "- $branch"; done
echo ""
echo "**Stale branches (>30 days):**"
stale=$(git for-each-ref --sort=committerdate refs/heads/ \
    --format='%(refname:short) %(committerdate:relative)' 2>/dev/null \
    | grep -E "(month|year)" | head -3)
[[ -n "$stale" ]] && echo "$stale" | while read -r line; do echo "- $line"; done || echo "_None_"
