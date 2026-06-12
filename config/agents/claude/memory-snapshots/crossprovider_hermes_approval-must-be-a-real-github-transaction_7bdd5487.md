---
name: crossprovider hermes approval-must-be-a-real-github-transaction
description: Approval must be a real GitHub transaction
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, github-state, governance]
---

Approval UX button cannot merely toggle UI state. Must transactionally: verify open GitHub issue, verify canonical plan in `docs/plans/`, verify no unresolved MAJOR review findings, create `.planning/plan-approved/<issue>.md` marker, flip label to `status:plan-approved`, comment on issue, refresh provider queue. Partial or missing steps leave ambiguous ownership.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
