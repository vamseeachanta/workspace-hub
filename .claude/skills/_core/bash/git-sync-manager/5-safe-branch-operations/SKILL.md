---
name: git-sync-manager-5-safe-branch-operations
description: 'Sub-skill of git-sync-manager: 5. Safe Branch Operations.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Safe Branch Operations

## 5. Safe Branch Operations


Switch branches safely across repositories:

```bash
#!/bin/bash
# ABOUTME: Safe branch switching across repositories
# ABOUTME: Validates branch existence and checks for uncommitted changes

switch_branch() {
    local repo="$1"
    local target_branch="$2"

    if [[ ! -d "$repo/.git" ]]; then
        echo "skip: not a git repo"
        return 1
    fi

    cd "$repo" || return 1

    # Check for uncommitted changes
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        echo "blocked: uncommitted changes"
        return 1
    fi

    # Check if branch exists locally
    if git show-ref --verify --quiet "refs/heads/$target_branch" 2>/dev/null; then
        git checkout "$target_branch" 2>/dev/null
        echo "switched: local branch"
        return 0
    fi

    # Check if branch exists remotely
    if git show-ref --verify --quiet "refs/remotes/origin/$target_branch" 2>/dev/null; then
        git checkout -b "$target_branch" "origin/$target_branch" 2>/dev/null
        echo "switched: created from remote"
        return 0
    fi

    echo "skip: branch not found"
    return 1
}

# Batch branch switch
batch_switch_branch() {
    local target_branch="$1"
    shift
    local repos=("$@")

    echo "Switching to branch: $target_branch"
    echo ""

    for repo in "${repos[@]}"; do
        echo -n "→ $repo: "
        switch_branch "$repo" "$target_branch"
    done
}
```
