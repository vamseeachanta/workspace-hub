---
name: crossprovider gemini formula-tests-require-parametric-direction-asser
description: Formula tests require parametric direction assertions
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, formulas, parametric-testing]
---

Value-only checks ('formula produces 5') miss direction errors (safety factor inversions, coefficient sign flips). Add assertions that outputs increase/decrease with parameter changes. Especially critical for doc-verified tests against standards.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
