---
name: crossprovider codex accounting-syntax-normalization-must-gate-on-cel
description: Accounting syntax normalization must gate on cell context
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [normalization-logic, context-awareness, domain-semantics]
---

Parenthesized numbers like `(130)` are normalized to `-130` as accounting format. This normalization was leaking into token-context comparisons where parentheses are prose, not accounting syntax, inflating document-lane agreement by matching parenthetical prose to negative values. Always require cell context before applying accounting transformations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
