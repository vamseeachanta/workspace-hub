---
name: crossprovider hermes adversarial-review-finds-orthogonal-test-gaps-st
description: Adversarial review finds orthogonal test gaps standard review misses
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-methodology, test-gaps, adversarial]
---

Sessions #2127/2128/2129 show adversarial reviews catching test gaps that standard reviews skip: env-mode caller tests, invalid-target atomicity, dupe-file cleanup. Standard reviews verify implemented behavior; adversarial reviews ask "what if the caller uses this wrong?" and surface missing coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
