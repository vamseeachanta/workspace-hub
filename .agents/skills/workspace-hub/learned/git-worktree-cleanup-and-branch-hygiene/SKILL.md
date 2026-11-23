---
name: git-worktree-cleanup-and-branch-hygiene
description: Systematic approach to cleaning up stale git worktrees, orphan branches, and branch hygiene at scale across multiple repos
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["git", "workflow", "automation", "repository-maintenance"]
---

# Git Worktree Cleanup and Branch Hygiene at Scale

When managing automation-heavy repos with accumulated stale worktrees and branches: (1) identify worktrees attached to merged branches via `git worktree list`, (2) remove them with `git worktree remove` before deleting branches (worktrees block deletion), (3) categorize remaining branches by lifecycle (worktree-agent remnants, orphan pre-restructure branches with no common ancestor, superseded feature branches, protected branches), (4) delete merged branches remotely first, then locally, (5) for unmerged branches with value, dry-run merges and resolve conflicts by keeping the current main version if divergence predates recent updates. This prevents disk bloat and merge conflicts from automation artifacts.