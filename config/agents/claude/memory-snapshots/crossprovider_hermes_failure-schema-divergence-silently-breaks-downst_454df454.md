---
name: crossprovider hermes failure-schema-divergence-silently-breaks-downst
description: Failure schema divergence silently breaks downstream consumers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [contracts, schema, backwards-compatibility]
---

Plans specifying failure output contracts (field names, required fields like tutorials/verification_method) drift in implementation. Mismatched field names (error_type vs error_summary) and missing fields are silent until a consumer tries to parse the output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
