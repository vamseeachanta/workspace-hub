---
name: crossprovider hermes approval-gates-correctly-block-autonomous-mutati
description: Approval gates correctly block autonomous mutation when artifacts missing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, safety, autonomous-execution]
---

When `.planning/plan-approved/<n>.md` is missing or plan body says 'NEEDS FRESH RE-REVIEW', Codex correctly skips implementation rather than mutating security/scheduled-task code. This shows approval-boundary enforcement working as intended—do not override when approval artifacts are inconsistent.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
