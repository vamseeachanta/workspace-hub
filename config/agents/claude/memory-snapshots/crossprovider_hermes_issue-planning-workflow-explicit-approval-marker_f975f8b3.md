---
name: crossprovider hermes issue-planning-workflow-explicit-approval-marker
description: Issue planning workflow: explicit approval marker + label sync before implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [issue-workflow, approval-gates]
---

Plan approval requires: (1) `.planning/plan-approved/<issue>.md` marker file created, (2) `status:plan-approved` label added + conflicting labels removed, (3) plan file status block changed from draft→plan-approved, (4) docs/plans/README.md row updated. Marker file is load-bearing; labels alone are not sufficient.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
