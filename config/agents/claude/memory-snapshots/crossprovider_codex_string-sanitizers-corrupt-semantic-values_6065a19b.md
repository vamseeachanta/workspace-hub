---
name: crossprovider codex string-sanitizers-corrupt-semantic-values
description: String sanitizers corrupt semantic values
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sanitization, semantic-corruption, validation]
---

Sanitizers that replace tokens (e.g., 'auth' -> '') uniformly across payloads can corrupt semantic values in structured fields like status enums and codes. Apply sanitization at field/structural boundaries, not as blanket string replacement on the entire payload.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
