---
name: crossprovider codex sparse-worktree-expansion-avoids-nesting-collisi
description: Sparse worktree expansion avoids nesting collision risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree-strategy, parallel-work]
---

When expanding a sparse-checkout worktree with missing tracked directories (src/, tests/), populate it in place rather than creating a nested worktree. Nesting adds isolation cost and collision risk on shared files during concurrent work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
