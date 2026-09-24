---
name: crossprovider gemini technical-document-classification-schema-for-sta
description: Technical document classification schema for standards and engineering documentation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [documentation, standards-taxonomy, asset-classification, metadata-schema]
---

Gemini classifies engineering standards, codes, and technical specifications using a standardized JSON schema: discipline (enum: structural|cathodic-protection|pipeline|marine|installation|energy-economics|materials|regulatory|drilling|other), summary (one-sentence scope), repos (prioritized subset of: digitalmodel, worldenergydata, assethold, lng-a, OGManufacturing, mkt-a), and keywords (3+ topic terms). Discipline selection drives repo relevance; only repos genuinely applicable are included.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
