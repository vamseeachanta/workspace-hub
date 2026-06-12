---
name: crossprovider hermes issue-planning-workflow-major-review-blocks-stat
description: Issue planning workflow: MAJOR review blocks status:plan-review label
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, issue-planning, gate]
---

When adversarial reviews return MAJOR verdict, issues must remain in `status:needs-plan` and plans must be revised + re-reviewed before they are approval-ready. Do NOT move to `status:plan-review` until round-N reviews clear. This is a hard gate, not advisory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
