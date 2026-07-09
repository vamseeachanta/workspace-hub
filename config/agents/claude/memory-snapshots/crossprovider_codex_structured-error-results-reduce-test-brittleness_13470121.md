---
name: crossprovider codex structured-error-results-reduce-test-brittleness
description: Structured error results reduce test brittleness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, api-design]
---

Unstructured string error results force tests to assert on substrings after joining, making tests brittle to formatting changes. Validation engines should return structured objects with fields like rule_id, path, line, summary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
