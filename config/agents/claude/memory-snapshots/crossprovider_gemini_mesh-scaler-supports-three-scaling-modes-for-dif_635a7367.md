---
name: crossprovider gemini mesh-scaler-supports-three-scaling-modes-for-dif
description: Mesh scaler supports three scaling modes for different use cases
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mesh-scaling, design-pattern, validation]
---

scale_mesh_uniform preserves aspect ratios; scale_mesh_parametric allows independent X/Y/Z factors for non-uniform deformation; scale_mesh_to_target matches specification dimensions. ScaleResult includes validation metrics (degenerate panels, aspect ratios, normal consistency) to catch mesh degradation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
