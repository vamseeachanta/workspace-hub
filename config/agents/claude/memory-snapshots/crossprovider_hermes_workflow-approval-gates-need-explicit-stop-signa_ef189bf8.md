---
name: crossprovider hermes workflow-approval-gates-need-explicit-stop-signa
description: Workflow approval gates need explicit stop signals, not silent deferral
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow-design, approval-gates, hermes-agent]
---

Plan-then-review-then-wait pattern requires clear markers: 'stop for user approval' before posting to GitHub, not continued planning cycles. Hermes alternates between planning and 'should I continue?' without a decisive stop gate. Embed STOP_FOR_APPROVAL comment/label in plan template to halt agent progression.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
