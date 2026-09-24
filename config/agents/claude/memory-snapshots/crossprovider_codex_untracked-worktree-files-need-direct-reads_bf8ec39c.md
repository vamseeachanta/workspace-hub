---
name: crossprovider codex untracked-worktree-files-need-direct-reads
description: untracked worktree files need direct reads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, review-patterns, worktrees]
---

`git diff` returns empty for untracked files in a worktree. When reviewing untracked implementation, read the files directly with line numbers rather than relying on `git diff` output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
