---
name: crossprovider codex stale-checkouts-with-active-mutations-require-is
description: Stale checkouts with active mutations require isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [git-workflow, safety, concurrency]
---

Rebasing or committing from a shared checkout that lags upstream and has active daemons (Deckhand) creates safety risks. Isolate on fresh upstream branch in a separate worktree to avoid contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
