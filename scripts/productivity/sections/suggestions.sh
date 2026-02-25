#!/usr/bin/env bash
# ABOUTME: Daily log section — productivity suggestions based on git/log patterns
# Usage: bash suggestions.sh <WORKSPACE_ROOT> <DAILY_LOG_DIR>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
DAILY_LOG_DIR="${2:-$WORKSPACE_ROOT/logs/daily}"
cd "$WORKSPACE_ROOT"

echo "### Productivity Suggestions"
echo ""

commits_today=$(git log --oneline --since="24 hours ago" 2>/dev/null | wc -l)
[[ $commits_today -gt 15 ]] && echo "- **Pattern:** High commit volume ($commits_today commits) — consider batching"
[[ $commits_today -eq 0 ]] && echo "- **Pattern:** No commits — review blockers or catch up on tasks"

uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
[[ $uncommitted -gt 10 ]] && echo "- **Action:** $uncommitted uncommitted changes — commit more frequently"

stale_count=$(git for-each-ref --sort=committerdate refs/heads/ \
    --format='%(committerdate:relative)' 2>/dev/null | grep -c -E "(month|year)" || true)
[[ $stale_count -gt 3 ]] && echo "- **Cleanup:** $stale_count stale branches — archive or delete"

logs_this_week=$(find "$DAILY_LOG_DIR" -name "*.md" -mtime -7 2>/dev/null | wc -l)
[[ $logs_this_week -lt 3 ]] && echo "- **Habit:** Only $logs_this_week daily logs this week — consistency builds productivity"
