---
name: crossprovider hermes adversarial-review-must-catch-plan-promised-feat
description: Adversarial review must catch plan-promised features absent from implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, adversarial-review, plan-fidelity]
---

Reviews comparing plan pseudocode against implementation code can surface significant gaps: e.g., plan promised working-tree root scanning but implementation only uses `git ls-files` (tracked files). Also document intended narrowing as design choice, not oversight.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
