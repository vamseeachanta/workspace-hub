---
name: crossprovider codex required-schema-fields-need-basis-context-not-ju
description: Required schema fields need basis/context, not just null-allowed
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema, contract, evidence]
---

Contract saying 'allow empty strings for unknown dates' does not prove dates were unknown. Use `null` plus required context fields like `source_data_latest_date_basis` (e.g., 'metadata_refresh', 'source_publication', 'unknown') and `unknown_reason` to enforce evidential gaps. Validators must reject missing basis when field is null.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
