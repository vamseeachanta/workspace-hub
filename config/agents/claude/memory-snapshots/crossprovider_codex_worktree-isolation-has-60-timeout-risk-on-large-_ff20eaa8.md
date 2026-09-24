---
name: crossprovider codex worktree-isolation-has-60-timeout-risk-on-large-
description: Worktree isolation has 60% timeout risk on large repos; reserve for commit/push only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, timeout-risk, agent-isolation]
---

Using isolation: worktree on large repos (~30K+ files) triggers timeouts in ~60% of runs. Reserve worktree isolation for agents that must commit/push; use main-session filesystem for general reads and file inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
