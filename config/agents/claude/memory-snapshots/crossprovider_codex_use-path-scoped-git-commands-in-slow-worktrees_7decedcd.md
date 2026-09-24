---
name: crossprovider codex use-path-scoped-git-commands-in-slow-worktrees
description: Use path-scoped git commands in slow worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, worktree-debugging]
---

Broad git operations like `git status` can hang indefinitely in this environment's slow worktrees. Use path-scoped commands (e.g., `git status <path>`) with timeouts to unblock validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
