---
name: crossprovider codex pinned-commit-verification-in-isolated-clones-fo
description: Pinned commit verification in isolated clones for concurrent work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [git-patterns, concurrent-work, verification]
---

When multiple sessions work on shared repositories, pin all reads/checks to specific commit objects (not mutable HEAD) and verify in isolated temporary clones. This prevents contamination from concurrent activity in shared worktrees and ensures reproducible audit results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
