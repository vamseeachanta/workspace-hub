---
name: git-worktree-workflow-execution-checklist
description: 'Sub-skill of git-worktree-workflow: Execution Checklist.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


| Step | Command | Verification |
|------|---------|--------------|
| Create worktree | `git worktree add -b <branch> <path> main` | `git worktree list` shows new entry |
| Navigate to worktree | `cd <path>` | `pwd` shows worktree path |
| Run Claude task | `claude "<task>"` | Task completes successfully |
| Commit changes | `git add . && git commit -m "message"` | `git log` shows commit |
| Return to main | `cd <main-project>` | `pwd` shows main path |
| Merge changes | `git merge <branch>` | `git log` shows merge |
| Remove worktree | `git worktree remove <path>` | `git worktree list` excludes entry |
| Delete branch | `git branch -d <branch>` | `git branch` excludes branch |
| Prune stale | `git worktree prune` | No stale references remain |
