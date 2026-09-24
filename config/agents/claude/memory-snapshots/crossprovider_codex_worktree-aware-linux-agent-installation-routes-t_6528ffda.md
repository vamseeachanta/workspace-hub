---
name: crossprovider codex worktree-aware-linux-agent-installation-routes-t
description: Worktree-aware Linux agent installation routes to primary checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktrees, linux, installation]
---

When installing persistent hotkeys or bindings from within a git linked worktree, detect the primary checkout and bind to that instead; the worktree is ephemeral. Use git worktree list and common-dir inspection to resolve install roots across linked worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
