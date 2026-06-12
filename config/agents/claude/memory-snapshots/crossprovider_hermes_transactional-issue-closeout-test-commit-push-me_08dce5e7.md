---
name: crossprovider hermes transactional-issue-closeout-test-commit-push-me
description: Transactional issue closeout: test→commit→push→merge→cleanup in one window, never separately
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, worktree-cleanup, issue-closeout]
---

Closing an issue first then deferring cleanup to a later sweep leaves stale branches, worktrees, and unmerged commits. Serialize all three (commit, push to origin, branch cleanup/merge/worktree removal) in the same closeout window using a repo-level lock/mutex. This is the only way to keep trees clean and work moving forward.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
