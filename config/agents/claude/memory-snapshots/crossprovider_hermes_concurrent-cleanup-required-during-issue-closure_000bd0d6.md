---
name: crossprovider hermes concurrent-cleanup-required-during-issue-closure
description: Concurrent cleanup required during issue closure for tree hygiene
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, issue-closure, workflow-design]
---

When an issue is closed, the cleanup (removing local branches, worktrees, resetting dirty state) and push to origin must happen concurrently/atomically. Sequential cleanup leaves stale artifacts behind; this is the only way to keep trees clean and work moving forward.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
