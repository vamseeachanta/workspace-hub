---
name: crossprovider gemini additive-data-transformation-with-separate-norma
description: Additive data transformation with separate normalized fields
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-design, normalization, auditability, enrichment]
---

When enriching or normalizing data, preserve original fields and emit separate normalized fields with accompanying metadata (version, method, status). This is more auditable and lets downstream consumers consciously choose which values to use rather than silently overwriting originals.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
