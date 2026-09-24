---
name: crossprovider codex sparse-checkout-can-exclude-tracked-files-breaki
description: Sparse-checkout can exclude tracked files, breaking full-suite collection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktree, testing, governance]
---

Isolated worktrees with sparse-checkout patterns may exclude tracked files from HEAD, causing test collection to fail mid-run before tests execute. This is not a local deletion; it is a scoped checkout limitation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
