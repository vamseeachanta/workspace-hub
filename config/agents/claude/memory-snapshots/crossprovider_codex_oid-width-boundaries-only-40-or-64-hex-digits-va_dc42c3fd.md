---
name: crossprovider codex oid-width-boundaries-only-40-or-64-hex-digits-va
description: OID width boundaries: only 40 or 64 hex digits valid
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, input-validation, oid]
---

Git object IDs must be 40 or 64 hex digits, never 41–63. Validate at input boundary (fail-closed) even though Git will catch later (fail-safe). Range inclusion accidentally accepts invalid widths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
