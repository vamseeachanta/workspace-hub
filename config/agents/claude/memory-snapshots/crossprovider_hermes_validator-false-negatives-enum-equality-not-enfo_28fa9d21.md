---
name: crossprovider hermes validator-false-negatives-enum-equality-not-enfo
description: Validator false negatives: enum/equality not enforced
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, schema-contract, false-negative]
---

Validator accepts invalid `node_id` (not matching `path`), unknown `kind` values (schema enumerates), `evidence_path` pointing to non-public scaffolding, and `duplicate_edge_count` not compared to actual edges. Schema declared constraints not validated.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
