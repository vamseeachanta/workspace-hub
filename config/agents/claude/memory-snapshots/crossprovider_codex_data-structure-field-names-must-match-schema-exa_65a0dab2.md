---
name: crossprovider codex data-structure-field-names-must-match-schema-exa
description: Data structure field names must match schema exactly (UK/US spelling, singular/plural)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-matching, silent-failures, field-naming]
---

Plan #607 mapped `--cog` to `center_of_gravity` when the schema defines `centre_of_gravity`; plan #609 had singular/plural mismatch on `radii_of_gyration` vs `radius_of_gyration`. Silent YAML failures result if names don't match the actual schema. Verify each mapped field name against input_schemas.py definitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
