---
name: crossprovider hermes approval-drift-blocker-github-label-vs-local-pla
description: Approval drift blocker: GitHub label vs local plan-marker mismatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, approval-gates, sidecar-pattern, codex-workflow]
---

When GitHub issue carries `status:plan-approved` label but local `.planning/plan-approved/<issue>.md` sidecar is missing AND the plan artifact still reads 'needs-re-review', the gate is BLOCKED. Autonomous agents must detect and refuse to cross this drift without explicit human decision to override. Approval markers must align across label + local artifact + plan content, or the mutation is gated.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
