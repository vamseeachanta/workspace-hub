---
name: crossprovider hermes adversarial-plan-review-catches-hardcoded-safety
description: Adversarial plan review catches hardcoded safety gaps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, planning-discipline, safety-validation]
---

llm-wiki issue #88 review found MAJOR blocking defects: plan was detection-only (separate validator) rather than prevention in normal generation, missed hardcoded fallback routes embedded in generator scripts, and tests asserted bad behavior instead of fixing it. Revision required code-level safe normalization + offline regression tests. This pattern applies to any route/dispatch system.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
