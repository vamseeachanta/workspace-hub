---
name: crossprovider hermes static-test-passes-mask-major-blockers-adversari
description: Static test passes mask MAJOR blockers; adversarial review is load-bearing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, testing-philosophy]
---

#2511 pytest showed 8/8 passed, but adversarial reviews (Gemini, Codex, Claude) independently found MAJOR issues: vacuous smoke, uncoupled decks, credibility risk, missing thermal validation. Test passes != portfolio credibility. Plan-review → adversarial → approval → TDD gate is not redundant.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
