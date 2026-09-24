---
name: crossprovider codex pytest-result-parsers-must-capture-both-failed-a
description: Pytest result parsers must capture both FAILED and ERROR node IDs as first-class failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, test-infrastructure, correctness]
---

Parsers that ignore ERROR lines will fail to catch new setup/collection/teardown errors even when they are listed in expected-failure catalogs. Both node types must be extracted with full parameterization syntax (e.g., `test[case-0]`) for exact-match filtering to work correctly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
