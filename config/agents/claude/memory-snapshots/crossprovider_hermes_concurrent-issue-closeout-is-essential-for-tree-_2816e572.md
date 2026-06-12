---
name: crossprovider hermes concurrent-issue-closeout-is-essential-for-tree-
description: Concurrent issue closeout is essential for tree hygiene
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, issue-closeout, concurrent-ops, worktree-hygiene]
---

When GitHub issues close, their cleanup/push operations must happen atomically/concurrently, not sequentially. Sequential closeout leaves stale branches, unmerged worktree commits, and uncleared files. User observed workspace-hub accumulating 100+ stale branches and dirty worktrees due to separation of closeout from issue-closure logic.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
