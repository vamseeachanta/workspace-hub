---
name: crossprovider codex multi-session-inspection-can-dirty-worktrees-in-
description: Multi-session inspection can dirty worktrees in shared checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [git-worktrees, concurrency, shared-state]
---

When inspecting a worktree in parallel-session environments, other concurrent sessions can modify files during read-only inspection. This is expected behavior in shared checkout scenarios; confirm file state before acting on inspection results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
