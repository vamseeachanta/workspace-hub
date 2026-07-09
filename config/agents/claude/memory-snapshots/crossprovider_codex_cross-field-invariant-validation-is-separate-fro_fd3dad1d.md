---
name: crossprovider codex cross-field-invariant-validation-is-separate-fro
description: Cross-field invariant validation is separate from individual field checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [validation, schema-design]
---

Validators often miss constraints like 'reconciliation_refs only valid for warning/blocker pairs, not compatible' or 'pair ID mapping must match configured left/right sources'. These require explicit checks after individual field validation passes, not inline during field checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
