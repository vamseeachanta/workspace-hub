---
name: crossprovider gemini multi-layer-skill-taxonomy-for-document-extracti
description: Multi-layer skill taxonomy for document extraction
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, skill-design, doc-extraction]
---

Structure complex extraction tasks into 3 independent layers: Layer 1 (generic content types: constants, equations, tables, curves, procedures, requirements, definitions, worked_examples), Layer 2 (engineering-pattern recognition), Layer 3 (domain-specific sub-skills like CP/drilling-riser/naval-architecture). Each layer is self-contained; domains inherit Layer 1 heuristics and add their own detection patterns. Enables reuse and composability across domains.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
