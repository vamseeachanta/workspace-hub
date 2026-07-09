---
name: crossprovider codex value-conditional-validation-weakens-security-bo
description: Value-conditional validation weakens security boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security, validation, schema-design]
---

Validators checking 'source term with digest-like value' still pass 'source term with placeholder value' and leak the term. Use fail-closed set membership instead of value-based checks at security boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
