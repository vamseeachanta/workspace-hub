---
name: crossprovider codex source-policy-verification-is-orthogonal-to-code
description: Source-policy verification is orthogonal to code review and test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [code-review, source-review, verification-methodology]
---

A test that validates "code rejects the entry" or "code defaults correctly" does not verify that the registry data is correctly sourced or accurately described. Code correctness (test passes) and source correctness (asserted facts match sources) require independent verification. Example: a test asserting "Viura fails strict conversion" is correct code; separately, the source description (Prospex/H&P = condensate-only, not density) must be verified against the PDF directly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
