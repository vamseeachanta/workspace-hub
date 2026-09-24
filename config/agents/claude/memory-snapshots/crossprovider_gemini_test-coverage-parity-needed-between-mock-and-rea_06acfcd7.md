---
name: crossprovider gemini test-coverage-parity-needed-between-mock-and-rea
description: Test coverage parity needed between mock and real codepaths
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [test-coverage, dual-mode-scripts, defect-pattern]
---

Dual-mode scripts (mock smoke-test shim vs real pytest) require separate test coverage for each path. If only mock path is tested, real path degrades silently until production. Pattern: test both `SMOKE_TEST_MODE=mock` and real pytest runs. Catch in code review: 'both paths tested?' checklist.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
