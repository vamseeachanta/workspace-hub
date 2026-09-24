---
name: crossprovider gemini disclosure-layer-only-contracts-avoid-multi-laye
description: Disclosure-layer-only contracts avoid multi-layer modification coupling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [design-pattern, architecture, contracts]
---

When defining ingestion/validation contracts, scope to a single layer rather than requiring changes to both new and legacy surfaces. Separate contracts by boundary to prevent mutation coupling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
