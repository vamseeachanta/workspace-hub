---
name: crossprovider hermes plan-approved-label-is-insufficient-load-bearing
description: Plan-approved label is insufficient load-bearing gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, approval-gates, plan-management]
---

`status:plan-approved` GitHub label alone does not guarantee approval readiness. Durable, revision-bound approval requires `.planning/plan-approved/<issue-id>.md` marker files in the repo. Used to distinguish truly approved plans from label-only claims when queue-triaging implementation targets.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
