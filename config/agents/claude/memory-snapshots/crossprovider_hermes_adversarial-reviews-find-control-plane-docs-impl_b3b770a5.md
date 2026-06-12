---
name: crossprovider hermes adversarial-reviews-find-control-plane-docs-impl
description: Adversarial reviews find control-plane docs/implementation gaps reliably
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-methodology, hermes, security, control-plane]
---

Multiple independent reviewers of #2720 found identical gaps: docs claim 'fail-closed' remote dispatch without evidence, but implementation accepts any self-asserted JSON; status `warn` + `dispatchable: true` contradict docs saying warn is non-dispatchable. Adversarial review before merge is load-bearing for control-plane code; architectural/semantic claims must survive defect-hunting, not just structural validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
