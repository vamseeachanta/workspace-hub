---
name: git-worktree-cleanup-at-scale
description: Identify and remove stale git worktrees blocking branch deletion in multi-repo environments
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["git", "worktree", "automation", "branch-hygiene", "multi-repo"]
---

# Git Worktree Cleanup at Scale

Worktrees are lightweight working directories sharing a `.git` store, useful for parallel agent work. However, stale worktrees block branch deletion and consume disk space. List active worktrees with `git worktree list`, identify ones on merged/obsolete branches, then remove with `git worktree remove <path>` before deleting the branch. This is especially critical in automation-heavy repos where agent sessions leave behind worktrees. Implement automated cleanup hooks to prevent accumulation.