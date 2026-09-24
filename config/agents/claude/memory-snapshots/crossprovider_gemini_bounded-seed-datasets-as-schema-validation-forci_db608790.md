---
name: crossprovider gemini bounded-seed-datasets-as-schema-validation-forci
description: Bounded seed datasets as schema validation forcing function
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [schema-design, api-v1, data-governance, scope-control]
---

Hard limits on initial data collection (e.g., <=12 records) force schema completeness and field-type decisions before sprawl. Use explicit row-count caps rather than open-ended collection targets; this prevents scope creep during v1 API foundation work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
