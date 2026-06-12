---
name: crossprovider hermes git-worktree-hooks-live-in-git-common-dir-not-gi
description: Git worktree hooks live in git-common-dir not git-dir
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktree, hooks, architecture]
---

In git worktrees, .git is a file (symlink to main repo), so .git/hooks/ doesn't exist. Hooks actually live in git-common-dir/hooks/. Hook path resolution must use `git rev-parse --git-common-dir` not `--git-dir` to find correct enforcement-env and hook paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
