---
name: crossprovider codex ast-based-function-line-counting-outperforms-sim
description: AST-based function-line counting outperforms simple line-count tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, ast, code-size-limits, verification]
---

Simple grep/wc for function-size limits (e.g., 50-line max) fail with multiline strings and docstrings. AST parsing provides accurate function spans. Use Python ast module or equivalent to verify code-size guardrails on generated/refactored code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
