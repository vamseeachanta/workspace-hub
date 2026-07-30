---
name: crossprovider codex finite-variant-encoding-scanning-has-algorithmic
description: Finite-variant encoding scanning has algorithmic bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [security, scanning, encoding]
---

Simple forbidden-value lists that check URL encoding (`%70`, `%7E`) and case variants are defeated by mixed-case hex escapes, unreserved-character encoding, and other syntactic variants. Use proper canonical normalization (e.g., full URL decode/re-encode) instead of enumerated variants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
