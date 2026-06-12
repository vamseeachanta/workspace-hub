---
name: crossprovider hermes approval-state-drift-live-github-labels-vs-local
description: Approval state drift: live GitHub labels vs local plan-approved markers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-labels, plan-gated, reconciliation]
---

Approval state tracked in two places: GitHub labels (live source via `gh issue view <#> --json labels`) and local `.planning/plan-approved/<n>.md` markers. Local markers can lag or diverge after user relabeling. Reconciliation step required before implementation: verify live labels match expected state, update local markers to current state, commit, then proceed to implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
