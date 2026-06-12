---
name: crossprovider hermes handoff-documentation-structure-enables-parallel
description: Handoff documentation structure enables parallel agent recovery
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [handoff, parallel-agents, recovery]
---

Durable handoff format: timestamp, machine name, repo path, branch, outcome summary, preserved worktrees, and restart checkpoints (open issue numbers, plan-review vs plan-approved states). Structure allows next session to resume work without re-exploring repo state or re-running discovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
