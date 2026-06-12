---
name: crossprovider hermes codex-bwrap-networking-rtm-newaddr-failure-block
description: Codex bwrap networking RTM_NEWADDR failure blocks execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex-sandbox, bwrap, apparmor, network-ns, blocker]
---

Codex sandbox execution fails with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` when attempting shell operations in worktrees. This blocks local validation/edit/commit/push on Codex lanes. AppArmor profile and network namespace restrictions appear to be the root cause; user should verify AppArmor config grants loopback networking to userns/bwrap.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
