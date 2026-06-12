---
name: crossprovider hermes github-labels-diverge-from-canonical-plan-state-
description: GitHub labels diverge from canonical plan state on readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-readiness, issue-state, github-labels, review-tracking]
---

Issues #2510 and #2346 showed `status:plan-approved` labels while canonical plan files said `status:plan-review` with blocking MAJOR findings. Label-only state is unreliable; always read the plan artifact and current review archive before assuming readiness. Divergence enables premature advancement and skipped blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
