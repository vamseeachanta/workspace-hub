---
name: crossprovider codex large-repo-worktree-checkout-may-go-quiet-but-is
description: Large repo worktree checkout may go quiet but is still progressing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [large-repos, worktrees, workflow-expectations]
---

digitalmodel and similar ~16k-file checkouts have long silent stretches where no progress is logged but I/O is still running. Interrupting causes partial worktree state cleanup burden; let checkout complete unless genuinely hung (check `fuser` or `lsof` first).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
