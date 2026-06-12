---
name: crossprovider gemini tdd-evidence-stratification-strong-vs-weak-vs-ab
description: TDD evidence stratification: strong vs weak vs absent
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, tdd, assessment]
---

When evaluating TDD discipline, distinguish three levels: STRONG (independent red-phase commit + green-phase commit with full evidence), WEAK (reusing pre-existing tests instead of writing new failing tests), ABSENT (dummy/padding tests like `echo test2` masquerading as real tests). Dummy tests are detectable by command type (echo vs pytest) and output absence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
