---
name: crossprovider hermes multi-round-same-provider-major-verdict-signals-
description: Multi-round same-provider MAJOR verdict signals fixability shift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-round-review, defect-classification, review-precision]
---

When single provider returns MAJOR in round 1 and MAJOR in round 2 on same artifact, that is not "give up"; it signals validator shallowness or fixability tier increased. R3 inline patches often resolve when precision improves. Example: #2747 truthy-vs-boolean blocker fixed by tightening gate definitions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
