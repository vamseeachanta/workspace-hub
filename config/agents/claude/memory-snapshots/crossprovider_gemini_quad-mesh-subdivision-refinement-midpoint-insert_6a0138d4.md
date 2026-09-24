---
name: crossprovider gemini quad-mesh-subdivision-refinement-midpoint-insert
description: Quad mesh subdivision refinement: midpoint insertion + vertex dedup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mesh-refinement, hydrodynamics, geometry]
---

Subdivide each quad into 4 sub-quads by inserting edge midpoints and center point. Create 4 new quads with CCW winding preserved. Deduplicate vertices via edge midpoint cache + np.unique after each level. Filter degenerate panels (area < 1e-6 m²). Each level multiplies panel count by 4.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
