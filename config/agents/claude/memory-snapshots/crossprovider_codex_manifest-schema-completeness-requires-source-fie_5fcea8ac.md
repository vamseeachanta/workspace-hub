---
name: crossprovider codex manifest-schema-completeness-requires-source-fie
description: Manifest schema completeness requires source-field traceability
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, data-contracts]
---

Plans defining manifest output fields must verify that every field has either: (1) an existing source field in the input schema, or (2) a documented derivation rule in pseudocode. Missing source traceability creates implementable-but-broken manifest specs where fields cannot be populated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
