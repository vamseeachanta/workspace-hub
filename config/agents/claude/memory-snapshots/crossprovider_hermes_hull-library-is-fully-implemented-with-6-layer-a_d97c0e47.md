---
name: crossprovider hermes hull-library-is-fully-implemented-with-6-layer-a
description: Hull library is fully implemented with 6-layer architecture, zero stubs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hull-library, hydrodynamics, implementation-status, architecture]
---

All 25 Python modules in digitalmodel/hydrodynamics/hull_library/ are fully implemented (7,656 lines, ~40 classes, ~150 functions) with zero stubs/NotImplementedError. Architecture: (1) Schema/Data (Pydantic models, RAO DB), (2) Mesh Generation (quad panelization, adaptive density), (3) Line Generator (4-phase pipeline: parser→surface→panelizer→exporter), (4) Mesh Manipulation (scaling, refinement, decimation with QEM algorithm), (5) Lookup/Query (spectral analysis, nearest-neighbor matching), (6) Visualization (pure-stdlib SVG). External deps: numpy, scipy, pydantic, yaml (required); plotly, pyvista, gmsh, pandas (optional, lazy-loaded).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
