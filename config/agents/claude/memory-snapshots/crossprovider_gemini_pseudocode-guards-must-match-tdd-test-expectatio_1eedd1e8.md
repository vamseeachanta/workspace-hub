---
name: crossprovider gemini pseudocode-guards-must-match-tdd-test-expectatio
description: Pseudocode guards must match TDD test expectations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tdd, pseudocode, test-implementation-coupling]
---

If TDD specifies `test_score_zero_sessions` expects `{status: "insufficient_data"}` on empty input, pseudocode must contain the guard clause. Missing guards cause silent failures: tests pass on fixtures but crash in production.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
