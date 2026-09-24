---
name: crossprovider codex multi-pass-adversarial-review-plan-code-implemen
description: Multi-pass adversarial review: plan → code → implementation, each with prior-finding verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-workflow, adversarial-review, quality-gates]
---

Plan review surfaces high-level defects (privacy/lifecycle/testability gaps), code review checks execution/artifact safety, implementation review validates that code/tests/artifacts match plan. After each pass, focused re-review on whether specific prior findings are resolved. Findings artifact documents each pass and blocks progression until resolved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
