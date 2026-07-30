---
name: crossprovider codex isolated-worktrees-for-parallel-issue-planning-p
description: Isolated worktrees for parallel issue planning prevents cross-contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [git-workflow, parallel-work, isolation]
---

When multiple issues are in flight (e.g., #252 CFD, #253 wet-period), each requires its own branch/worktree for planning. Shared checkout with parallel edits causes git state confusion and blocks correct plan review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
