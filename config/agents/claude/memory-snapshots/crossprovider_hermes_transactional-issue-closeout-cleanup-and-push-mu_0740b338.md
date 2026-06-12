---
name: crossprovider hermes transactional-issue-closeout-cleanup-and-push-mu
description: Transactional issue closeout: cleanup and push must be concurrent, not deferred
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, issue-closure, debt-prevention]
---

When closing an issue, cleanup (branch deletion, worktree removal, state verification) and push to origin must happen in the same transaction: commit → push → merge/sync → branch disposition → worktree removal → clean proof → close issue. Deferring cleanup creates accumulated stale branches, unmerged commits, and uncleaned worktrees that compound in future sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
