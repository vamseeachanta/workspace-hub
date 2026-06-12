---
name: crossprovider hermes self-referential-plan-approval-gates-cause-block
description: Self-referential plan approval gates cause blocker loops
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-design, approval-gate-logic, self-reference-hazard]
---

Plans that self-define acceptance criteria like 'fresh re-review required with git SHA + local-vs-main marker' will fail their own gate if review artifacts lack those metadata fields. The plan blocks itself. Approval gates must reference external/independent acceptance criteria, not plan-internal metadata.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
