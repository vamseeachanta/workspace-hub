---
name: crossprovider gemini routing-contracts-must-explicitly-distinguish-cu
description: Routing contracts must explicitly distinguish curated (trusted) from raw (auto-generated) surfaces
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [routing, indexing, contracts]
---

Indexing and routing contracts need separate enumerations for canonical/curated entry points vs auto-generated noise. #2460 tier-1 contract gap was knowing which per-repo surfaces are trustworthy. A routing contract must name both classes and their roles (trusted for discovery, raw for audit).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
