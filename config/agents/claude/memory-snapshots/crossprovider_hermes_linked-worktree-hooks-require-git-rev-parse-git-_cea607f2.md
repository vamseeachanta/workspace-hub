---
name: crossprovider hermes linked-worktree-hooks-require-git-rev-parse-git-
description: Linked-worktree hooks require git rev-parse --git-path, not .git/hooks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktrees, hooks, path-resolution]
---

Worktree `.git` is a file (gitlink), not a directory. Plans hard-coding `.git/hooks/pre-push` fail in linked worktrees. Use `git rev-parse --git-path hooks` or respect `core.hooksPath` config. Tests must validate on real linked-worktree layouts, not just main checkout.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
