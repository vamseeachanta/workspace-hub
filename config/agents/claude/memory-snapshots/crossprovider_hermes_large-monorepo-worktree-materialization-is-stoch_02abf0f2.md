---
name: crossprovider hermes large-monorepo-worktree-materialization-is-stoch
description: Large monorepo worktree materialization is stochastically slow under load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-hub, worktree-performance]
---

workspace-hub 19k+ file worktree creation variance: 17min typical, 60+ min under parallel-agent I/O. Add 5min heartbeat polling; if dir absent after deadline, kill + pivot to alternate strategy (serial execution or isolated clone).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
