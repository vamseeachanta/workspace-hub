---
name: crossprovider hermes adversarial-review-execution-compliance-gap
description: Adversarial review execution compliance gap
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-gates, compliance-gap, enforcement]
---

Review infrastructure (gates, hooks, scripts) is strong (8/10), but execution is weak: 4% of commits show git-level enforcement, 10% show cross-review evidence (30-day), 58% artifact compliance. The gates exist and fire, but developers aren't reliably going through review before push. Gap is enforcement—gates are advisory (Level 0 in policy, though Level 3 hooks exist).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
