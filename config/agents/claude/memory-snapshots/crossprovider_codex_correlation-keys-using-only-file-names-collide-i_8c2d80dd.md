---
name: crossprovider codex correlation-keys-using-only-file-names-collide-i
description: Correlation keys using only file names collide in amend and concurrent-worktree scenarios
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, collision-risk, concurrent-worktrees]
---

A 5-second time window + branch + file-name digest does not prevent collisions when the same files are committed twice, amended, or touched concurrently in multiple worktrees. Add either content-hash correlation or accept `collision: unknown` in the spec.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
