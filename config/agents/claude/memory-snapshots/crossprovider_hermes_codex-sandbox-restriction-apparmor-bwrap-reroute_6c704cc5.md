---
name: crossprovider hermes codex-sandbox-restriction-apparmor-bwrap-reroute
description: Codex sandbox restriction: AppArmor bwrap reroute pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-reroute, codex-sandbox, apparmor]
---

When Codex fails with 'bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted', AppArmor blocks nested userspace network setup. Safe reroute: post comment, remove `agent:codex`, add `agent:claude`, relaunch Claude on same worktree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
