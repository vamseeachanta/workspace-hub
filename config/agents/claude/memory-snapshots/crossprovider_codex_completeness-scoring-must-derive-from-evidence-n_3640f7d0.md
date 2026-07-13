---
name: crossprovider codex completeness-scoring-must-derive-from-evidence-n
description: Completeness scoring must derive from evidence, never self-certify
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [review, scoring, artifact-quality]
---

Avoid hardcoded or self-reported completeness booleans (e.g., `completeness_score = 5/5 hardcoded`). Instead, derive the score from actual test pass/fail, scan output, verification results, and absence proofs. Adversarial review will reject self-certifying metrics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
