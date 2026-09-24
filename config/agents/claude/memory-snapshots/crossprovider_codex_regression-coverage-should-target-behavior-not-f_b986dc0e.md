---
name: crossprovider codex regression-coverage-should-target-behavior-not-f
description: Regression coverage should target behavior, not file partitioning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, regression-testing, brittle-tests]
---

Plans requiring exact file names or YAML key strings as regression criteria are brittle when the actual contract is behavioral (model loads, exports, contains metadata). Over-specification ties tests to internal implementation details. Regression tests should assert observable behavior unless file/key structure IS the actual contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
