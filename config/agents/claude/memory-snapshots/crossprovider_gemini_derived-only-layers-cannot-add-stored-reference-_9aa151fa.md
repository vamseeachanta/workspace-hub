---
name: crossprovider gemini derived-only-layers-cannot-add-stored-reference-
description: Derived-only layers cannot add stored reference fields
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-architecture, schema-design]
---

When adding derived views/calculations, the 'derived-only' boundary means: preserve originals unchanged, emit separate new fields, don't add stored foreign-key references to source tables, and don't mutate the underlying data. If the change requires a new stored field, it's not derived-only.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
