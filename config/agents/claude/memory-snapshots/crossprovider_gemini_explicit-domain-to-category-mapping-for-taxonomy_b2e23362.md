---
name: crossprovider gemini explicit-domain-to-category-mapping-for-taxonomy
description: Explicit domain-to-category mapping for taxonomy hierarchies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [taxonomy, schema, mapping]
---

Taxonomies at scale (16 filesystem domains mapping to 12 category indexes) require explicit mapping documentation before schema implementation. Do not assume 1:1 correspondence. Missing mapping leaves 4 domains unallocated and causes reviewer confusion. Define mapping in schema step before any scripting.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
