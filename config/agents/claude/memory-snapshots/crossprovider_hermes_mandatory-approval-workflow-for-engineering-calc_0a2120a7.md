---
name: crossprovider hermes mandatory-approval-workflow-for-engineering-calc
description: Mandatory approval workflow for engineering calculations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-workflow, approval-gates, issue-planning]
---

Non-trivial engineering work (e.g., ship hydrodynamic reports #2760) follows a formal gate sequence: resource intel → draft plan in `workspace-hub/docs/plans/` → adversarial review → post summary to GH → set `status:plan-review` → wait for user approval. Implementation never starts before approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
