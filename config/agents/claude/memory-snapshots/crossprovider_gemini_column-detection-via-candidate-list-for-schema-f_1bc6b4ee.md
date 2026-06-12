---
name: crossprovider gemini column-detection-via-candidate-list-for-schema-f
description: Column detection via candidate list for schema flexibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [schema-adaptation, data-mapping, robustness]
---

When mapping legacy/vendor data to schema, use candidate lists (e.g. `_OIL_VOL_CANDIDATES = ["MON_O_PROD_VOL", "OIL_STB", "OIL_PROD_VOL"]`) to handle schema variation. First match wins; fallback to None if none found. Reduces brittle field-name coupling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
