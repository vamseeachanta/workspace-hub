---
name: crossprovider hermes git-worktree-detection-via-git-filesystem-check-
description: Git worktree detection via `.git` filesystem check is brittle
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktree, filesystem-checks]
---

In git worktrees, `.git` is a file (ref to actual .git/worktrees/<name>) not a directory. Code checking `os.path.isdir('.git')` fails to detect worktrees as valid git repos. Use `git rev-parse --is-inside-work-tree` instead of filesystem checks for robust worktree support.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
