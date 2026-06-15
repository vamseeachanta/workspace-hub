---
name: crossprovider codex back-compat-wrappers-must-explicitly-guard-negat
description: Back-compat wrappers must explicitly guard negative/zero values
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, back-compat, guards, type-safety]
---

Do not rely on schema validation to reject negative block_coefficient; wrapper must check `if profile.block_coefficient and profile.block_coefficient > 0` before passing to schema, else new validation breaks old callers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
