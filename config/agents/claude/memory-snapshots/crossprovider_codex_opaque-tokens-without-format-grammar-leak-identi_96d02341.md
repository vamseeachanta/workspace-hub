---
name: crossprovider codex opaque-tokens-without-format-grammar-leak-identi
description: Opaque tokens without format grammar leak identifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [token-design, identifier-leakage, interface-contracts]
---

Tokens designed as 'opaque' but without explicit grammar can leak private identifiers if derived from paths or client names. Opaque-by-contract requires explicit forbidden patterns: ban raw path fragments, extensions, client words.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
