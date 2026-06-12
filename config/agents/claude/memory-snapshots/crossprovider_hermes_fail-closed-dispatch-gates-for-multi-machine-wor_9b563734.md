---
name: crossprovider hermes fail-closed-dispatch-gates-for-multi-machine-wor
description: Fail-closed dispatch gates for multi-machine work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, safety, multi-machine, fail-closed]
---

Dispatch blocks on any of: dirty worktree, unpushed commits, unavailable host, unauthorized user, failed workflow gate. All conditions must pass; single failure is terminal. No partial/escalation dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
