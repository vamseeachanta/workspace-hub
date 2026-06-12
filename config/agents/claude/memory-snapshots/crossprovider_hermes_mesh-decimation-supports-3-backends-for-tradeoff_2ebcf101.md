---
name: crossprovider hermes mesh-decimation-supports-3-backends-for-tradeoff
description: Mesh decimation supports 3 backends for tradeoff between deps and speed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [mesh-generation, decimation, optional-dependencies, algorithm-portability]
---

Hull library decimation modules (decimation.py, decimation_vtk.py, decimation_gmsh.py) implement the same Quadric Error Metric (QEM) algorithm with 3 optional backends: pure NumPy (always available, slower), VTK (optional, GPU-accelerated), GMSH (optional, high quality). Developers can choose based on available dependencies and performance requirements without rewriting the caller code.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
