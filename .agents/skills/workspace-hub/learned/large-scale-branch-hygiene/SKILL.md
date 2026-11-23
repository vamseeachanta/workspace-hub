---
name: large-scale-branch-hygiene
description: Systematic approach to cleaning stale branches across multiple repos while preserving active work
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["git", "branch-management", "multi-repo", "maintenance"]
---

# Large-Scale Branch Hygiene Workflow

When managing many repos with accumulated stale branches: (1) inventory all repos and categorize branches (worktree artifacts, orphaned histories, merged-upstream), (2) identify patterns (e.g., `archive/*` branches from restructurings that can't merge), (3) use dry-runs to verify before mass deletion, (4) handle protected branches separately and verify API errors aren't transient, (5) stash active work, merge valuable unmerged branches, clean merged branches, then restore stash. Key insight: pull latest before merge attempts—upstream may have already merged branches you think are local.