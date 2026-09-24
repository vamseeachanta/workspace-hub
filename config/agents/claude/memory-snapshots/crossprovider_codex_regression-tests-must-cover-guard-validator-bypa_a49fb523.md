---
name: crossprovider codex regression-tests-must-cover-guard-validator-bypa
description: Regression tests must cover guard/validator bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, validators]
---

When testing guards or validators (e.g., a mypy command contract that rejects `src/` in the target list), include regression tests that attempt to bypass the guard, not just happy-path cases. Example: test both 'src/ as first arg' and 'src/ appended after targeted files'. A validator that only rejects the first-position case misses the append bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
