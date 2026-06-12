---
name: crossprovider codex worktree-isolation-per-publisher-in-parallel-ing
description: Worktree isolation per publisher in parallel ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [architecture, ingest, isolation]
---

Each publisher's ingest batch runs in its own `git worktree add` so codex sandbox workspace-write covers it cleanly; simplifies cleanup and prevents cross-publisher state bleed when parallelizing at the publisher level.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
