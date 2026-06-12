---
name: crossprovider hermes adversarial-review-verdicts-don-t-auto-converge
description: Adversarial review verdicts don't auto-converge
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, verdict, consensus]
---

Sessions repeatedly see Claude APPROVE, Codex MAJOR, Gemini MINOR on same plan. Conditional logic like 'if MAJOR=0 then post' waits forever. Must surface consensus-vs-minority explicitly and force user re-decision before proceeding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
