---
name: crossprovider codex automatic-worktree-deletion-has-unavoidable-toct
description: Automatic worktree deletion has unavoidable TOCTOU race
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [worktree-safety, concurrency-limits, automation-safety]
---

Pre-delete recheck and process scan cannot prevent another agent from entering a worktree between verification and deletion. Daily automated pruning is unsafe; at most produce a non-mutating candidate report. Worktree lifecycle automation needs repository-wide leases or a two-phase quarantine with recoverable grace periods.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
