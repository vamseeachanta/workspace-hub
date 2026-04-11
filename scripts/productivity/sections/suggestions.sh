#!/usr/bin/env bash
# ABOUTME: Daily log section — actionable suggestions based on repo/project state
# Usage: bash suggestions.sh <WORKSPACE_ROOT> <DAILY_LOG_DIR>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
DAILY_LOG_DIR="${2:-$WORKSPACE_ROOT/logs/daily}"

echo "### Suggestions"
echo ""

suggestions=()

# --- Collect repos: hub + submodules ---
repos=("$WORKSPACE_ROOT")
if [[ -f "$WORKSPACE_ROOT/.gitmodules" ]]; then
    while IFS= read -r line; do
        if [[ "$line" =~ path\ =\ (.+) ]]; then
            repos+=("$WORKSPACE_ROOT/${BASH_REMATCH[1]}")
        fi
    done < "$WORKSPACE_ROOT/.gitmodules"
fi

# --- 1. Dirty repos (uncommitted changes) ---
dirty_repos=()
for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
        status=$(cd "$repo" && timeout 5 git status --porcelain 2>/dev/null | head -1 || true)
        if [[ -n "$status" ]]; then
            dirty_repos+=("$(basename "$repo")")
        fi
    fi
done
if [[ ${#dirty_repos[@]} -gt 0 ]]; then
    suggestions+=("**Commit dirty work**: $(IFS=', '; echo "${dirty_repos[*]}") have uncommitted changes")
fi

# --- 2. Unpushed commits ---
unpushed_repos=()
for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
        count=$(cd "$repo" && timeout 5 git rev-list --count '@{u}..HEAD' 2>/dev/null || echo "0")
        if [[ "$count" -gt 0 ]] 2>/dev/null; then
            unpushed_repos+=("$(basename "$repo") has $count commits not pushed to origin")
        fi
    fi
done
if [[ ${#unpushed_repos[@]} -gt 0 ]]; then
    for item in "${unpushed_repos[@]}"; do
        suggestions+=("**Push unpushed commits**: $item")
    done
fi

# --- 3. Stale daily logs (not reviewed) ---
if [[ -d "$DAILY_LOG_DIR" ]]; then
    recent_logs=$(find "$DAILY_LOG_DIR" -maxdepth 1 -name '*.md' -o -name '*.yaml' -o -name '*.yml' | sort -r | head -5)
    unreviewed=0
    for log_file in $recent_logs; do
        if [[ -f "$log_file" ]] && ! grep -q 'reviewed: true' "$log_file" 2>/dev/null; then
            unreviewed=$((unreviewed + 1))
        fi
    done
    if [[ $unreviewed -gt 0 ]]; then
        suggestions+=("**Review daily logs**: Last $unreviewed daily logs not marked as reviewed")
    fi
fi

# --- 4. Work queue items ---
pending_wrk=0
for wrk_file in "$WORKSPACE_ROOT"/logs/daily/wrk-*.yaml "$WORKSPACE_ROOT"/logs/daily/wrk-*.yml "$WORKSPACE_ROOT"/logs/daily/wrk-*.json; do
    if [[ -f "$wrk_file" ]]; then
        pending_wrk=$((pending_wrk + 1))
    fi
done
if [[ $pending_wrk -gt 0 ]]; then
    suggestions+=("**Work queue**: $pending_wrk pending work-queue file(s) in logs/daily/")
fi

# --- Output ---
if [[ ${#suggestions[@]} -eq 0 ]]; then
    echo "_Everything looks clean!_"
else
    for s in "${suggestions[@]}"; do
        echo "- $s"
    done
fi
