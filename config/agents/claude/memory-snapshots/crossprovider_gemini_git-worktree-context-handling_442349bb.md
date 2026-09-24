---
name: crossprovider gemini git-worktree-context-handling
description: Git worktree context handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, shell, paths]
---

When temp working directories may be outside repo, use `git -C <repo-root> show <sha>` instead of bare `git show` to ensure correct repo context resolution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
