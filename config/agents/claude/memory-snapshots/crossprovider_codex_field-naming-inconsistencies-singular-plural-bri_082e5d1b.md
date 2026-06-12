---
name: crossprovider codex field-naming-inconsistencies-singular-plural-bri
description: Field naming inconsistencies (singular/plural, British/American spelling) silently drop data
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-validation, cli-design]
---

Plan #607 maps CLI `--rog` to `vessel.inertia.radius_of_gyration` (singular, American), but the schema field is `radii_of_gyration` (plural, British). Schema validation will drop the field silently. Verify all field names against the actual schema before writing CLI mappings; don't rely on naming conventions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
