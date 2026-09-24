---
name: crossprovider gemini data-source-registry-for-centralized-governance
description: Data source registry for centralized governance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-governance, metadata, pattern]
---

Maintain a single source-registry file (YAML or config) that catalogs all data sources with URLs, licenses, update frequencies, and dataset hierarchies. This decouples source metadata from extraction logic and simplifies bulk updates when sources move or change.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
