---
name: multi-repo-branch-hygiene-at-scale
description: Systematic approach to cleaning stale branches, resolving merge conflicts, and syncing multiple repos
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["git", "multi-repo", "workflow", "branch-management", "cleanup"]
---

# Multi-Repo Branch Hygiene at Scale

When managing 17+ repos with accumulating stale branches: (1) Identify patterns (worktree branches, orphan histories, protected branch errors) across all repos in parallel; (2) Resolve merge conflicts by checking if HEAD (main) is more current than the feature branch, then prefer HEAD for safe resolution; (3) For each dirty repo, commit changes to main, push, and clean up merged branches locally and remotely; (4) Use stash/restore workflow to preserve uncommitted work during branch operations. Large repos (58MB+ git index) will have slow `git status` — proceed with other repos in parallel rather than blocking.