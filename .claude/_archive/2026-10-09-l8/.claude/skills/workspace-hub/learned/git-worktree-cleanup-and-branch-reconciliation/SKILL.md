---
name: git-worktree-cleanup-and-branch-reconciliation
description: Systematic process for cleaning up stale git worktrees, resolving merge conflicts in diverged branches, and reconciling branch state across multiple repositories.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["git", "workflow", "branch-management", "multi-repo"]
---

# Git Worktree Cleanup and Branch Reconciliation

When managing multiple repos with stale branches and orphaned worktrees: (1) Identify worktrees attached to merged/stale branches using `git worktree list`, (2) Remove stale worktrees with `git worktree remove` to unblock branch deletion, (3) Categorize remaining branches (merged, feature-complete, orphaned from history rewrites), (4) For branches with unmerged content, pull latest main first to detect upstream merges, then resolve conflicts by keeping HEAD (main) on surrounding files while preserving the branch's actual fix logic, (5) Delete superseded branches and verify all repos are clean. Key insight: Worktrees block deletion and consume disk; history rewrites create "no common ancestor" branches that can't merge.