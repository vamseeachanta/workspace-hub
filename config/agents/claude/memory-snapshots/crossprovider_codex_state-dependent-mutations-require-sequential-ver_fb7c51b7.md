---
name: crossprovider codex state-dependent-mutations-require-sequential-ver
description: State-dependent mutations require sequential verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency-safety, git-workflows]
---

When mutations depend on prior GitHub state changes (e.g., close issues only after PR merges), use single-lane execution with verification between each step. Parallel attempts break the dependency chain.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
