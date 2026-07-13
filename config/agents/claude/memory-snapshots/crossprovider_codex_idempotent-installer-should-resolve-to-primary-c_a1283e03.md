---
name: crossprovider codex idempotent-installer-should-resolve-to-primary-c
description: Idempotent installer should resolve to primary checkout, not linked worktree
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [installer, git-worktree, idempotency, symlink-strategy]
---

When running from a linked git worktree, detect this and resolve to the primary checkout using `git worktree list --porcelain`. Create symlinks and hotkeys pointing to the persistent primary, not the temporary or session-specific worktree. Prevents the hotkey from becoming stale when the worktree is deleted or moved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
