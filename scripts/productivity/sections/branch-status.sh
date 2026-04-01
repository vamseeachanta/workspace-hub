#!/usr/bin/env bash
# ABOUTME: Daily log section — stale branch report across all repos
# Usage: bash branch-status.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
STALE_DAYS=14

echo "### Branch Status"
echo ""

repos=("$WORKSPACE_ROOT")
if [[ -f "$WORKSPACE_ROOT/.gitmodules" ]]; then
    while IFS= read -r line; do
        if [[ "$line" =~ path\ =\ (.+) ]]; then
            repos+=("$WORKSPACE_ROOT/${BASH_REMATCH[1]}")
        fi
    done < "$WORKSPACE_ROOT/.gitmodules"
fi

stale_count=0
repo_count=0
now=$(date +%s)

echo "| Repo | Branch | Age (days) | Merged | Status |"
echo "|------|--------|-----------|--------|--------|"

for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
        repo_name=$(basename "$repo")
        main_branch=$(cd "$repo" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
        branches=$(cd "$repo" && timeout 8 git for-each-ref --format='%(refname:short) %(committerdate:unix)' refs/heads/ 2>/dev/null || true)
        has_branch=false
        while IFS= read -r entry; do
            [[ -z "$entry" ]] && continue
            branch="${entry% *}"
            epoch="${entry##* }"
            [[ "$branch" == "$main_branch" || "$branch" == "main" || "$branch" == "master" ]] && continue
            has_branch=true
            age_days=$(( (now - epoch) / 86400 ))
            merged=$(cd "$repo" && git branch --merged "$main_branch" 2>/dev/null | tr -d ' ' | grep -qx "$branch" && echo "yes" || echo "no")
            status=""
            if (( age_days >= STALE_DAYS )); then
                status="stale"
                stale_count=$((stale_count + 1))
            fi
            echo "| $repo_name | $branch | $age_days | $merged | $status |"
        done <<< "$branches"
        [[ "$has_branch" == true ]] && repo_count=$((repo_count + 1))
    fi
done

echo ""
echo "**$stale_count stale branches across $repo_count repos**"
