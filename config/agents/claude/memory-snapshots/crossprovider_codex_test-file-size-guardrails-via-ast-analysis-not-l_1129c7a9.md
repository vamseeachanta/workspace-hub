---
name: crossprovider codex test-file-size-guardrails-via-ast-analysis-not-l
description: Test file size guardrails via AST analysis, not line counting
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, guardrails, metrics, ast]
---

File and function size guardrails (e.g., 400-line file, 50-line function) can be enforced via AST analysis, which is immune to formatting and counts semantic units, not display lines. More reliable than simple line counting for detecting oversized blocks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
