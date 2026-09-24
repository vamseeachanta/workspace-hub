---
name: crossprovider gemini fleet-format-mapping-discipline-names-mandatory-
description: Fleet format mapping discipline: names, mandatory fields, strict filtering
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [fleet-mapping, data-quality, schema-conversion]
---

When converting between fleet schemas, preserve both original and mapped field names (e.g., RIG_NAME alongside VESSEL_NAME). Explicitly set mandatory fields (DATA_SOURCE, VESSEL_CATEGORY, HULL_FORM_TYPE, IS_OFFSHORE). Apply strict filtering: remove null/empty name entries and malformed patterns (e.g., 'NON RIG' strings).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
