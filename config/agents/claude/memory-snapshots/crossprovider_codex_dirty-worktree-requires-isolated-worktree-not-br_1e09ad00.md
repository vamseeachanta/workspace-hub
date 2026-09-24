---
name: crossprovider codex dirty-worktree-requires-isolated-worktree-not-br
description: Dirty worktree requires isolated worktree, not branch strategy alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [worktree, git-safety, dirty-state]
---

A 92-file dirty tree cannot be safely handled by creating a branch off main; must create isolated worktree from origin/main with explicit owned/forbidden paths and pre-edit status capture to avoid contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
