---
name: crossprovider hermes partial-git-staging-creates-unsafe-commits-must-
description: Partial git staging creates unsafe commits; must restage after worktree changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, commit-safety, code-review, workspace-hub]
---

When index shows `AM` (added-modified) but worktree receives later fixes post-staging, staged versions miss new changes. Commit is unsafe. Verify `git diff --cached` vs. `git diff` before final commit; restage all affected files if worktree is newer. Prevents landing stale staged code.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
