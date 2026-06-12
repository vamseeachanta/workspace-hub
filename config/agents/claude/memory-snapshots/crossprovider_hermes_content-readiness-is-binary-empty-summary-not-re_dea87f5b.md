---
name: crossprovider hermes content-readiness-is-binary-empty-summary-not-re
description: Content readiness is binary: empty summary = not ready for approval
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [content-readiness, binary-gates, wiki-approval]
---

Plans claiming 'new wiki coverage exists' but with handoff artifact `ready_for_X: false` and empty `summary` fields signal content is unverified. Approval requires non-empty, domain-verified summary in both handoff + acceptance evidence. This defect class appears across wiki/standards workflows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
