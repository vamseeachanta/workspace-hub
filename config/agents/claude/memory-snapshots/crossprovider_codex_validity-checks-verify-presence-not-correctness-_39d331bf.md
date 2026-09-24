---
name: crossprovider codex validity-checks-verify-presence-not-correctness-
description: Validity checks verify presence, not correctness — check `if key in dict` instead of validating value format
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-rigor, proof-validation, manifest-integrity]
---

Validators often check whether required keys exist (digest present, field_counts present) without validating their correctness (hex format, consistency with row counts, alignment with actual data). Malformed evidence passes silently. Validate both structure and content integrity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
