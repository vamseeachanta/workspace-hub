---
name: crossprovider codex git-status-hangs-in-shared-worktrees-use-bounded
description: Git status hangs in shared worktrees; use bounded queries
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-workaround, shared-checkout]
---

`git status -z -uall` can hang for minutes in large shared checkouts. Use bounded queries instead: `git log`, `git diff`, `git branch -v`, or direct file inspection to avoid triggering full index walks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
