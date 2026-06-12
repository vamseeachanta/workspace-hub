---
name: crossprovider gemini mesh-geometry-operations-require-degenerate-pane
description: Mesh geometry operations require degenerate-panel validation after coordinate transformation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [computational-geometry, validation, mesh-processing]
---

After scaling or refining a panel mesh, validate quality metrics: aspect ratios, degenerate panel count (area < threshold), and bounding box consistency. Aspect-ratio distribution reveals pathological refinement (e.g., too-thin slivers after non-uniform scaling); degenerate count flags topology corruption.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
