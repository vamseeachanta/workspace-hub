#!/usr/bin/env bash
# ABOUTME: Daily log section — git activity summary across all repos
# Usage: bash git-summary.sh <WORKSPACE_ROOT> <since_date>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
SINCE_DATE="${2:-yesterday}"

echo "### Git Activity"
echo ""

total_commits=0
repos=("$WORKSPACE_ROOT")
if [[ -f "$WORKSPACE_ROOT/.gitmodules" ]]; then
    while IFS= read -r line; do
        if [[ "$line" =~ path\ =\ (.+) ]]; then
            repos+=("$WORKSPACE_ROOT/${BASH_REMATCH[1]}")
        fi
    done < "$WORKSPACE_ROOT/.gitmodules"
fi

for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
        repo_name=$(basename "$repo")
        commits=$(cd "$repo" && git log --oneline --since="$SINCE_DATE" 2>/dev/null | head -10)
        count=$(cd "$repo" && git log --oneline --since="$SINCE_DATE" 2>/dev/null | wc -l)
        if [[ -n "$commits" ]]; then
            echo "**$repo_name** ($count commits)"
            echo '```'
            echo "$commits"
            echo '```'
            echo ""
            total_commits=$((total_commits + count))
        fi
    fi
done

[[ $total_commits -eq 0 ]] && echo "_No commits in the specified period_" && echo ""
echo "**Total commits:** $total_commits"
