---
name: crossprovider hermes batch-packs-require-separate-worktrees-for-safe-
description: Batch packs require separate worktrees for safe concurrent execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [batch-execution, parallelization, git-safety, worktree-isolation]
---

Packs reading the same source registries must not run in parallel within a shared worktree; git state interference causes silent mutations and merged deltas. Each parallel pack execution needs isolation: worktree or explicit branch separation. Safe only when pack scopes do not share branches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
