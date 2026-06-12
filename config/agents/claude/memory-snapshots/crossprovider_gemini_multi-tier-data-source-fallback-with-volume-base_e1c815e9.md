---
name: crossprovider gemini multi-tier-data-source-fallback-with-volume-base
description: Multi-tier data source fallback with volume-based winner selection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, data-collection, fallback-chain]
---

When integrating data from multiple sources per entity, evaluate sources in priority order (live web → cached scrape → hardcoded defaults), selecting the source with the most records per operator. Avoids data gaps while biasing toward completeness.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
