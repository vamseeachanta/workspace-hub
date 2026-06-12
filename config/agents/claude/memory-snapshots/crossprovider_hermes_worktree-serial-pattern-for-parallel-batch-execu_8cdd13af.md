---
name: crossprovider hermes worktree-serial-pattern-for-parallel-batch-execu
description: Worktree + serial pattern for parallel batch execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git-contention-avoidance, worktree-pattern]
---

For long nightly batches across multiple repos, use worktrees for execution isolation (T1/T2/T3 execution terminals) and serial planning in a dedicated terminal (T4) for shared-target docs. This prevents git lock contention while parallelizing independent work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
