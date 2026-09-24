---
name: crossprovider codex git-commands-hang-in-shared-worktrees-under-conc
description: Git commands hang in shared worktrees under concurrent activity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree, concurrency, performance]
---

When `git` porcelain commands (status, commit, log) hang in shared 10-thread worktrees with parallel lane activity, use bounded timeouts and fall back to Git plumbing (`commit-tree` + `update-ref`) or GitHub API queries. Avoids blocking execution and provides verifiable evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
