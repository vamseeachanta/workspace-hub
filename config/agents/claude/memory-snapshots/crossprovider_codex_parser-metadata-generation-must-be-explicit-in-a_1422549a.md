---
name: crossprovider codex parser-metadata-generation-must-be-explicit-in-a
description: Parser metadata generation must be explicit in API contract
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, provenance, documentation]
---

When a parser (e.g., parse_cores_frame) returns a DataFrame but downstream components need provenance metadata (which field used a source, which defaulted, audit trail), the metadata generation must be explicitly specified in the function's contract and return value, not left to implicit handling in adapter/report layers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
