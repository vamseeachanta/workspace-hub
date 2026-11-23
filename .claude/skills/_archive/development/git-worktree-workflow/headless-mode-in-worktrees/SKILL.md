---
name: git-worktree-workflow-headless-mode-in-worktrees
description: 'Sub-skill of git-worktree-workflow: Headless Mode in Worktrees.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Headless Mode in Worktrees

## Headless Mode in Worktrees


```bash
# Automate worktree operations
WORKTREE="../project-auto-$(date +%s)"
git worktree add -b auto-task "$WORKTREE" main

cd "$WORKTREE"
claude -p "Complete the task in task.md" --output result.md

# Collect results
cp result.md ../results/
git worktree remove "$WORKTREE"
```
