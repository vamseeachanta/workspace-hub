---
name: crossprovider codex large-repos-need-gitignore-for-worktree-director
description: Large repos need .gitignore for worktree directories to avoid traversal noise
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, performance, hygiene, worktrees]
---

In repos with ~16k tracked files and slow checkout (e.g., digitalmodel), ensure `.worktrees/` is in `.gitignore` to prevent full untracked traversal noise. Use `git ls-files` or `git diff --name-only` instead of `git status` when traversal is slow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
