---
name: crossprovider codex stray-orphan-worktrees-corrupt-subsequent-isolat
description: Stray orphan worktrees corrupt subsequent isolation assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [worktrees, isolation, cleanup, state-management]
---

Dedicated issue worktrees (e.g., ~/.config/superpowers/worktrees/issue-23) can be left in broken state (missing .git, stray files). Prefer canonical main checkout when user explicitly specifies it. Clean up orphan worktrees explicitly on exit to avoid poisoning future isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
