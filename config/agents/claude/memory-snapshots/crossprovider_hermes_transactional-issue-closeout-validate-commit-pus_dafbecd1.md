---
name: crossprovider hermes transactional-issue-closeout-validate-commit-pus
description: Transactional issue closeout: validate/commit/push/comment/label in one window
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [issue-lifecycle, git-workflow]
---

Do not close an issue first, then clean up later. Closeout must be atomic: validation + commit + push + evidence comment + label updates + branch/worktree cleanup all in one transaction. Incomplete closeouts leave orphaned branches and stale traces.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
