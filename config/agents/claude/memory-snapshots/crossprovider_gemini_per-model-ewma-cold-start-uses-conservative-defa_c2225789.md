---
name: crossprovider gemini per-model-ewma-cold-start-uses-conservative-defa
description: Per-model EWMA cold-start uses conservative default_priority/25
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [routing, adaptive-selection, cold-start]
---

When routing to untested model variants, avoid over-allocation with aggressive priors. Cold-start EWMA score is default_priority/25; add +0.3 capability bonus only if model tier matches task tier. This prevents premature selection of expensive models on low-confidence tasks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
