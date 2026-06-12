---
name: crossprovider hermes plan-approved-workflow-label-committed-marker-gi
description: Plan-approved workflow: label + committed marker + GitHub handoff comment
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, governance, approval-gates]
---

GitHub issue approval for implementation requires three artifacts: (1) `status:plan-approved` label on the issue, (2) committed marker file at `.planning/plan-approved/<issue-id>.md`, (3) GitHub handoff comment linking issue to approval marker. All three prevent accidental re-planning and signal execution readiness. Validated across #2665 approval cycle.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
