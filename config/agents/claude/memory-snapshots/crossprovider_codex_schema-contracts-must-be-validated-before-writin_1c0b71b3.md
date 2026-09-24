---
name: crossprovider codex schema-contracts-must-be-validated-before-writin
description: Schema contracts must be validated before writing downstream pseudocode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-contract, pseudocode-verification, cross-file-consistency]
---

Sessions #607, #609, #611 found that plans assume schema fields/enums that don't exist or work differently than pseudocode claims (length_units vs units, xz+yz vs both, vessel+bodies mutual exclusion). Grep the actual schema file for field names, valid enum values, and validation logic before writing CLI pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
