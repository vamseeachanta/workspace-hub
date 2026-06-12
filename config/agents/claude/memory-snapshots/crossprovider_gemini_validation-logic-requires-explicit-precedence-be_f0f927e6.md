---
name: crossprovider gemini validation-logic-requires-explicit-precedence-be
description: Validation logic requires explicit precedence between signal types
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [validation, precedence, design, clarity]
---

When multiple evidence types exist (explicit keywords, branch naming, labels, body mentions), precedence order must be documented. Substring matching alone is too loose; need clear token semantics and tie-break rules (#2506).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
