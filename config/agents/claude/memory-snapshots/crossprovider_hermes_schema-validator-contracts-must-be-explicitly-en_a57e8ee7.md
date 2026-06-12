---
name: crossprovider hermes schema-validator-contracts-must-be-explicitly-en
description: Schema validator contracts must be explicitly enforced in code
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, validation, contract-drift]
---

Public graph validator accepts artifacts that violate schema requirements: `node_id != path`, invalid `kind` enum values, missing summary fields like `public_safety_note` and `high_degree_threshold`, and `eligible_page_count` mismatch. Schema doc and validator code diverged. Fix: add explicit checks for each contract in validator and negative tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
