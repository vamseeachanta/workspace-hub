---
name: crossprovider gemini additive-layering-preserves-original-fields-thro
description: Additive layering preserves original fields through derivation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-architecture, auditability, normalization]
---

When adding normalized/comparable/derived fields to records, preserve original as-reported values completely unchanged. Both layers coexist; mutation of originals loses provenance and prevents later policy changes without data loss.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
