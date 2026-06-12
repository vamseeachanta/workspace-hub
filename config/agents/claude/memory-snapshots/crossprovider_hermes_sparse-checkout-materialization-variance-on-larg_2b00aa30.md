---
name: crossprovider hermes sparse-checkout-materialization-variance-on-larg
description: Sparse checkout materialization variance on large repos requires active monitoring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, performance, workspace-hub]
---

Workspace-hub worktree materialization shows 1-60+ min variance under parallel I/O load. Sanity-check worktree dir presence at 5min mark; if absent, kill+pivot to avoid hung sessions. Variance driven by parallel-agent I/O contention, not just file count.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
