---
name: crossprovider hermes stale-plan-detection-readme-md-issue-status-row-
description: Stale plan detection: README.md issue-status row is the approval ledger
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-status, approval-ledger, stale-detection]
---

Plans' approval readiness is determined by `docs/plans/README.md` row status (values: plan-review, approval-ready, execution, completed). Plans claiming approval but with status='plan-review' in README are contradicted by ground truth. Always check README row before believing plan metadata.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
