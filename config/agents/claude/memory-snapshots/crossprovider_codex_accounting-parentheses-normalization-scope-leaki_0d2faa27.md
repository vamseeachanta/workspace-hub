---
name: crossprovider codex accounting-parentheses-normalization-scope-leaki
description: Accounting parentheses normalization scope leaking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [accounting-normalization, context-boundary, scope-leakage]
---

Numeric normalization that treats parenthetical notation as accounting-negative syntax (e.g., `'(130)'` → `-130`) can leak outside its intended cell context, causing spurious agreement between text tokens and negated numeric values when `cell=False`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
