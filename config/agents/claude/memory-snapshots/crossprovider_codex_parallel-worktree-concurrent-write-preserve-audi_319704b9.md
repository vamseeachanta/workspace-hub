---
name: crossprovider codex parallel-worktree-concurrent-write-preserve-audi
description: Parallel worktree concurrent-write: preserve, audit, merge from remote tip
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [concurrency, git-workflow, parallel-agents]
---

When multiple agents modify the same planning/config worktree, preserve all commits (no force-push/reset), audit divergence independently, and create integration branch from remote tip to reconcile safely. Never race for the same file; always audit concurrent state before advancing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
