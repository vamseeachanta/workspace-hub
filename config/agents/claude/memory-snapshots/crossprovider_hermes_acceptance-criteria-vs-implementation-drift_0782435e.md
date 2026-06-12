---
name: crossprovider hermes acceptance-criteria-vs-implementation-drift
description: Acceptance criteria vs implementation drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-process, acceptance-criteria, governance-gap]
---

Plan acceptance docs (e.g., 'redacted client IDs') vs staged diff can contradict silently. Plan review passes but implementation publishes literal client paths. Adversarial review must explicitly diff acceptance criteria against staged artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
