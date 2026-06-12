---
name: crossprovider hermes git-worktree-git-is-a-file-pointer-not-a-directo
description: Git worktree .git is a file pointer, not a directory
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktrees, paths]
---

In a worktree, `.git` is a text file pointing to `.git/worktrees/<name>`, not a directory. Filesystem checks like `path.exists()` return true but path resolution under `.git/hooks/` fails. Use `git rev-parse --git-path` to resolve hook paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
