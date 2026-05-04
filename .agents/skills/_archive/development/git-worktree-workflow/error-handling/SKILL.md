---
name: git-worktree-workflow-error-handling
description: 'Sub-skill of git-worktree-workflow: Error Handling.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Error | Cause | Solution |
|-------|-------|----------|
| Branch already checked out | Branch exists in another worktree | Remove existing worktree or use different branch |
| Cannot remove worktree | Uncommitted changes present | Commit, stash, or force remove |
| Permission errors | Directory not writable | `chmod -R u+w <worktree>` then remove |
| Stale worktree references | Worktree directory deleted manually | Run `git worktree prune` |
| Lock file exists | Previous operation interrupted | Remove `.git/worktrees/<name>/locked` file |
| Path already exists | Directory exists at target path | Choose different path or remove existing directory |
