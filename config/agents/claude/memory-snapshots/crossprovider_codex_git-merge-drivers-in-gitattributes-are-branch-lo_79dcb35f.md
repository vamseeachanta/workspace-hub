---
name: crossprovider codex git-merge-drivers-in-gitattributes-are-branch-lo
description: Git merge drivers in .gitattributes are branch-local and must be pre-adopted
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, merge-drivers, parallel-dispatch, worktree-setup]
---

Merge drivers (e.g., merge=union for append-only files) are read from the branch's tree BEFORE the merge starts, not from the merge's content. If a branch was created before .gitattributes contained the driver spec, subsequent merges won't activate it even if origin/main has it now. In parallel multi-stage dispatch where child worktrees are created after parent branches, adopt .gitattributes immediately after every worktree creation (before any merge), not just before the final origin/main merge. Fix: run `git checkout origin/main -- .gitattributes && git commit` right after `add_worktree()` returns, for every publisher branch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
