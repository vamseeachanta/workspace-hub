---
name: crossprovider hermes overnight-batch-prompts-need-explicit-worktree-g
description: Overnight batch prompts need explicit worktree + git coordination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-batching, worktree-management]
---

Parallel batch runs require: (1) deterministic prompt files written to /tmp before launch, (2) fresh worktrees from origin/main per issue, (3) stale .git/worktrees entries cleaned beforehand. Incomplete worktree cleanup caused timeouts; git worktree prune + explicit origin/main branch isolation is mandatory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
