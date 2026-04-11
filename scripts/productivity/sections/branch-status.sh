#!/usr/bin/env bash
# ABOUTME: Daily log section — branch divergence status across all repos (hub + submodules)
# Usage: bash branch-status.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"

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

has_divergence=false
table_rows=()

for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
        repo_name=$(basename "$repo")
        branch=$(cd "$repo" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        tracking=$(cd "$repo" && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo "")

        ahead=0
        behind=0
        if [[ -n "$tracking" ]]; then
            counts=$(cd "$repo" && git rev-list --left-right --count HEAD..."@{upstream}" 2>/dev/null || echo "0	0")
            ahead=$(echo "$counts" | awk '{print $1}')
            behind=$(echo "$counts" | awk '{print $2}')
        fi

        if [[ $ahead -gt 0 ]] || [[ $behind -gt 0 ]]; then
            has_divergence=true
        fi

        tracking_display="${tracking:-none}"
        table_rows+=("| $repo_name | $branch | $ahead | $behind | $tracking_display |")
    fi
done

if [[ ${#table_rows[@]} -gt 0 ]]; then
    echo "| Repo | Branch | Ahead | Behind | Tracking |"
    echo "|------|--------|-------|--------|----------|"
    for row in "${table_rows[@]}"; do
        echo "$row"
    done
    echo ""
fi

if [[ "$has_divergence" == false ]]; then
    echo "_All branches in sync with origin_"
fi
