---
name: crossprovider codex partial-worktree-cleanup-after-failed-checkout
description: Partial worktree cleanup after failed checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, worktree, recovery]
---

If `git worktree add` dies mid-progress (e.g., mount timeout), an unregistered partial directory + new branch remain. Delete ONLY the partial dir (`rm -rf <partial>`); reuse the branch for a fresh `git worktree add` attempt. Do not try to recover the incomplete checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
