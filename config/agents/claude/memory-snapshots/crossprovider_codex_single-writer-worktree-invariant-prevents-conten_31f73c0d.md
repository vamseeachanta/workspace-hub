---
name: crossprovider codex single-writer-worktree-invariant-prevents-conten
description: Single-writer worktree invariant prevents contention
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [worktree, concurrency, git]
---

Only one Codex session should edit a worktree at a time. Parallel sessions cause git index slowness, test timeouts, and duplicate process chains. Stop stale processes immediately; verify solo ownership before edits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
