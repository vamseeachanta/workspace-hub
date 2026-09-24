---
name: crossprovider codex validate-numeric-fields-before-aggregation-bucke
description: Validate numeric fields before aggregation bucketing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [aggregation, data-quality, parsing]
---

In numeric aggregation, parse and validate all fields BEFORE creating the result bucket. Premature bucket creation leaves orphan zero-valued rows when parsing fails, which masquerade as valid data and corrupt output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
