---
name: crossprovider codex parallel-read-only-workspace-scans-use-targeted-
description: Parallel read-only workspace scans: use targeted probes, not full-tree traversals
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, parallelization, performance, read-only]
---

When multiple agents do read-only searches on large shared trees like `/mnt/ace`, broad full-tree commands create I/O contention and duplicate work. Use targeted repo/directory probes instead, scoping by likely subdirectories (e.g., `worldenergydata`, `aceengineercode`) and avoiding uninterruptible full-tree traversals that multiple sessions can pile onto simultaneously.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
