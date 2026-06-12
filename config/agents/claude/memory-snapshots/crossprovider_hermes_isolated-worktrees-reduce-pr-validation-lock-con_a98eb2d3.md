---
name: crossprovider hermes isolated-worktrees-reduce-pr-validation-lock-con
description: Isolated worktrees reduce PR validation lock contention
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, pr-validation, git-lock, isolation]
---

Creating a worktree from origin/main for branch/PR mergeability checks avoids blocking main checkout and allows safe rollback if conflicts appear. Preferred over using main checkout for validation-heavy workflows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
