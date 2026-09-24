---
name: crossprovider codex ephemeral-worktree-artifacts-need-transience-mar
description: Ephemeral worktree artifacts need transience markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [worktree-hygiene, handoff-clarity, local-state]
---

When agents create worktree state, `/tmp/` files, or `.planning/` draft directories during a session, mark them explicitly as transient so future sessions and handoffs don't treat them as durable repo state. Without markers, cleanup work becomes a recurring burden.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
