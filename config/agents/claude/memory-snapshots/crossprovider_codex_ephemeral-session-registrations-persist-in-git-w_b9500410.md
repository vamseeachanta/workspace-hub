---
name: crossprovider codex ephemeral-session-registrations-persist-in-git-w
description: Ephemeral session registrations persist in git worktree list
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [worktrees, session-cleanup, registry, stale-state]
---

Worktrees registered under /tmp/claude-* (session-scoped, removed after session end) remain in `git worktree list` indefinitely. Registry is never auto-pruned. Cleanup audits must scan and prune stale entries independently of filesystem presence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
