---
name: crossprovider codex scheduled-publication-requires-explicit-precondi
description: Scheduled publication requires explicit preconditions and exit codes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [automation-safety, publication, scheduled-tasks]
---

Plans proposing git commits, scheduled automation, or automated publication repeatedly lack: worktree cleanliness check, concurrent-run prevention, required-input precondition, exit-code contract (dry-run vs publication vs degraded). Publication tasks need all four before pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
