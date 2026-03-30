---
name: git-advanced-1-interactive-rebase
description: 'Sub-skill of git-advanced: 1. Interactive Rebase (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Interactive Rebase (+1)

## 1. Interactive Rebase


**Basic Interactive Rebase:**
```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Rebase onto main
git rebase -i main

# Rebase from specific commit
git rebase -i abc123^
```

**Interactive Rebase Commands:**
```
pick   abc123 First commit     # Use commit as-is
reword def456 Second commit    # Edit commit message
edit   ghi789 Third commit     # Stop to amend
squash jkl012 Fourth commit    # Combine with previous
fixup  mno345 Fifth commit     # Combine, discard message
drop   pqr678 Sixth commit     # Remove commit
```

**Common Rebase Workflows:**
```bash
# Squash all commits into one
git rebase -i main
# Change all but first 'pick' to 'squash'

# Reorder commits
git rebase -i HEAD~3
# Rearrange the pick lines

# Split a commit
git rebase -i HEAD~3
# Change 'pick' to 'edit' on target commit
git reset HEAD^
git add -p  # Add pieces
git commit -m "First part"
git add .
git commit -m "Second part"
git rebase --continue

# Edit commit message
git rebase -i HEAD~3
# Change 'pick' to 'reword'
```

**Autosquash Pattern:**
```bash
# Create fixup commit
git commit --fixup=abc123

# Create squash commit
git commit --squash=abc123

# Apply autosquash
git rebase -i --autosquash main

# Enable autosquash by default
git config --global rebase.autosquash true
```


## 2. Git Worktrees


**Basic Worktree Usage:**
```bash
# List worktrees
git worktree list

# Add worktree for existing branch
git worktree add ../feature-branch feature/new-feature

# Add worktree with new branch
git worktree add -b hotfix/urgent ../hotfix-urgent main

# Remove worktree
git worktree remove ../feature-branch

# Prune stale worktrees
git worktree prune
```

**Worktree Workflow:**
```bash
# Project structure
workspace/
├── main/           # Main development
├── feature-auth/   # Feature branch
├── hotfix-critical/# Hotfix branch
└── experiment/     # Experimental work

# Setup
cd main
git worktree add ../feature-auth feature/authentication
git worktree add ../hotfix-critical -b hotfix/critical-bug
git worktree add ../experiment -b experiment/new-approach

# Work on feature
cd ../feature-auth
# make changes...
git commit -am "Add authentication"

# Quick switch to fix bug
cd ../hotfix-critical
# fix bug...
git commit -am "Fix critical bug"
git push

# Back to feature
cd ../feature-auth
```

**Worktree Helper Script:**
```bash
#!/bin/bash
# scripts/worktree.sh
# ABOUTME: Git worktree management helper
# ABOUTME: Simplifies creating and managing worktrees

set -e

WORKTREE_BASE="${WORKTREE_BASE:-$(dirname $(git rev-parse --git-dir))}"

case "$1" in
    add)
        BRANCH="$2"
        DIR="${3:-$WORKTREE_BASE/../$(echo $BRANCH | tr '/' '-')}"
        if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
            git worktree add "$DIR" "$BRANCH"
        else
            git worktree add -b "$BRANCH" "$DIR"
        fi
        echo "Created worktree at: $DIR"
        ;;
    remove)
        git worktree remove "$2"
        ;;
    list)
        git worktree list
        ;;
    *)
        echo "Usage: $0 {add|remove|list} [branch] [directory]"
        exit 1
        ;;
esac
```
