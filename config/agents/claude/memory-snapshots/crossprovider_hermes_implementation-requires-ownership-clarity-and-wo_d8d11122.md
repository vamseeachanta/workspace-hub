---
name: crossprovider hermes implementation-requires-ownership-clarity-and-wo
description: Implementation requires ownership clarity and worktree isolation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [concurrency, worktree-isolation, ownership-gates]
---

Parallel agent work is unsafe without explicit ownership collision check or isolated worktree state. Before starting implementation, verify no other worker owns the issue and confirm clean or isolated worktree state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
