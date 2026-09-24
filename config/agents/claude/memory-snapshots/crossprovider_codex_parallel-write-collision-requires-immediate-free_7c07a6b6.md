---
name: crossprovider codex parallel-write-collision-requires-immediate-free
description: Parallel write collision requires immediate freeze and preservation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, git-hygiene, multi-agent-safety]
---

When a parallel writer contaminates a supposedly isolated implementation worktree, freeze all writes immediately and preserve the contaminated state for owner investigation. Use a clean branch for repairs to prevent propagation to downstream tasks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
