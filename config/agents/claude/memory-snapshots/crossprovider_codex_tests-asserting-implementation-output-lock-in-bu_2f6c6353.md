---
name: crossprovider codex tests-asserting-implementation-output-lock-in-bu
description: Tests asserting implementation output lock in bugs when spec diverges
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, specifications, llm-wiki]
---

Tests written to verify actual implementation output (not spec requirements) can enshrine bugs. When implementation and spec diverge, tests pass falsely. In spec-heavy systems like llm-wiki, separate spec-compliance tests (verify requirements met) from output-format tests (verify structure).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
