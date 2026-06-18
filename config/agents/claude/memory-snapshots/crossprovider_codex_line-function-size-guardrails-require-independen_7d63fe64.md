---
name: crossprovider codex line-function-size-guardrails-require-independen
description: Line/function size guardrails require independent AST validation outside tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [code-style, guardrails, testing, ast-validation]
---

Functions exceeding 50-line limits and files exceeding 400 lines pass test suites but violate runtime style guardrails. Need separate AST-based size checks independent of test coverage to validate these constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
