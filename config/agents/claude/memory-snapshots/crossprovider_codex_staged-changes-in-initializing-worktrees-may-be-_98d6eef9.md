---
name: crossprovider codex staged-changes-in-initializing-worktrees-may-be-
description: Staged changes in initializing worktrees may be incomplete state, not real work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git, worktree, workflow]
---

When using `git worktree` to check for competing implementations, a locked or initializing worktree's staged changes (index) may reflect incomplete initialization rather than actual implementation in progress. Verify implementation status via commit ancestry (`git merge-base`) and direct ref queries instead of relying on `git status` output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
