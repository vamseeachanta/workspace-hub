---
name: crossprovider hermes approval-gate-requires-dual-transaction-label-co
description: Approval gate requires dual transaction: label + committed marker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-gates, implementation-readiness]
---

GitHub `status:plan-approved` label alone is not sufficient; implementation requires a committed marker file (e.g., `.planning/plan-approved/<issue>.md`) in the repo. Both must exist for implementation to proceed. Label without marker or marker without label is incomplete.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
