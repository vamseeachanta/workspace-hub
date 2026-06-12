---
name: crossprovider hermes adversarial-review-pre-closeout-catches-staged-f
description: Adversarial review pre-closeout catches staged/fixture/validation gaps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-gate, adversarial-review, closeout-gating]
---

MAJOR review verdicts surface critical gaps (staged ≠ working tree, non-deterministic artifacts, incomplete validation) that code review misses. Run adversarial review before closeout approval; MAJOR blocks closeout until fixes are applied and staged.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
