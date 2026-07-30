---
name: crossprovider codex evidence-only-vs-accepted-for-conversion-is-a-fi
description: Evidence-only vs accepted-for-conversion is a first-class field state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [registry-design, fail-closed, field-classification]
---

Fields with range evidence or industry sources must be marked explicitly (accepted_for_conversion=false, api_gravity_deg=null, bbl_per_tonne=null) and retained in source_gap_fields. Strict mode must fail closed for evidence-only fields; default-only mode must opt in explicitly and be tested separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
