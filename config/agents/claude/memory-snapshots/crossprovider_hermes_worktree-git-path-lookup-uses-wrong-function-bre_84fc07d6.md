---
name: crossprovider hermes worktree-git-path-lookup-uses-wrong-function-bre
description: Worktree git-path lookup uses wrong function, breaks hook discovery
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-worktree, shell-safety, hook-discovery]
---

Git worktrees have `.git` as a file pointing to `.git/worktrees/<name>`, with hooks under `.git/worktrees/<name>/hooks/` ONLY for worktree-specific hooks. Shared hooks live under the main `.git/hooks/` (the git-common-dir). Using `git rev-parse --git-dir` in a worktree returns the worktree path, not common-dir, causing enforcement-env lookups to fail silently. Use `git rev-parse --git-common-dir` for portable hook discovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
