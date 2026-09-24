---
name: crossprovider gemini three-mode-mesh-scaling-design-uniform-parametri
description: Three-mode mesh scaling design (uniform + parametric + target)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mesh-processing, cfd, design-pattern]
---

When implementing mesh transformations, support three independent scaling modes: uniform (single factor), parametric (independent X/Y/Z factors), and target-dimension-based (scale to reach L/B/D goals). This provides flexibility for different use cases without complicating the core algorithm.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
