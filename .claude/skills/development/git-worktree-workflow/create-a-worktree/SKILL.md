---
name: git-worktree-workflow-create-a-worktree
description: 'Sub-skill of git-worktree-workflow: Create a Worktree (+2).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Create a Worktree (+2)

## Create a Worktree


```bash
# Create worktree for existing branch
git worktree add ../project-feature feature-branch

# Create worktree with new branch
git worktree add -b new-feature ../project-new-feature main

# Create worktree for detached HEAD (testing)
git worktree add --detach ../project-test HEAD
```

## List Worktrees


```bash
git worktree list
# Output:
# /project           abc1234 [main]
# /project-feature   def5678 [feature-a]
# /project-hotfix    ghi9012 [hotfix-123]
```

## Remove Worktree


```bash
# Remove after merging
git worktree remove ../project-feature

# Force remove (discards changes)
git worktree remove --force ../project-abandoned

# Prune stale worktrees
git worktree prune
```
