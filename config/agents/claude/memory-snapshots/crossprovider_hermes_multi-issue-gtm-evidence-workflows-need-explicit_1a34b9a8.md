---
name: crossprovider hermes multi-issue-gtm-evidence-workflows-need-explicit
description: Multi-issue GTM evidence workflows need explicit sequencing and ownership rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gtm, plan-review, dependencies, workflow-sequencing]
---

When evidence fill (#2560), classification (#2562), and parent updates (#2554) are interdependent, the plan must explicitly state whether work is serial, parallel, or conditional, which issue owns the blocker-update gate, and whether unblocking parent #2554 requires re-review after child evidence lands. Absence of sequencing rules causes scope overlap and duplicate ownership claims.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
