---
name: crossprovider codex parallel-codex-processes-in-shared-worktree-will
description: Parallel Codex processes in shared worktree will race on file edits
metadata:
  type: reference
  source: codex
  bridged: 2026-08-05
  tags: [parallelism, worktree-safety, multi-agent]
---

Multiple Codex instances can execute against the same worktree branch simultaneously. Check parallel-work state before writing; if another process is active on target files, wait for completion and verify its landing before appending. Races corrupt both the work and the session state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
