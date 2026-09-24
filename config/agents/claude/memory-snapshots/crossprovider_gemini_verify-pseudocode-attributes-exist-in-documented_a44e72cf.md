---
name: crossprovider gemini verify-pseudocode-attributes-exist-in-documented
description: Verify pseudocode attributes exist in documented event schema
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pseudocode, schema-validation, correctness]
---

Pseudocode that references `e.next_gap_seconds` or `e.type` must verify these fields actually exist in the documented corpus. Fabricated attributes cause runtime AttributeError crashes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
