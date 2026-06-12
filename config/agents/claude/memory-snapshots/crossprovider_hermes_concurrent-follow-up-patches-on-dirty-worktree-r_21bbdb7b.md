---
name: crossprovider hermes concurrent-follow-up-patches-on-dirty-worktree-r
description: Concurrent follow-up patches on dirty worktree risk silent state loss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-state-management, hermes-orchestration, concurrent-automation]
---

Launching multiple plan-patch sessions in rapid succession (e.g., timestamps 1535, 1649, 1712 same cron run) while worktree has uncommitted changes from prior patches can silently lose edits or create undetected conflicts. Serialize patch launches or isolate via separate worktrees.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
