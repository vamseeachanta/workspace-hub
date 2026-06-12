---
name: crossprovider hermes parametric-sweep-is-full-stack-pipeline-geometry
description: Parametric sweep is full-stack pipeline: geometry→GDF→BEM→RAO→database
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parametric-analysis, hydrodynamics, workflow-orchestration, BEM-integration]
---

The parametric_hull_analysis.sweep module orchestrates end-to-end: (1) Expands SweepConfig (13 wave/geometry/solver params) into parametric space using hull_library's HullParametricSpace; (2) Generates quad meshes for each variant via HullMeshGenerator; (3) Exports to GDF format; (4) Runs BEM via Capytaine integration; (5) Computes RAOs; (6) Classifies depth (DEEP/MEDIUM/SHALLOW/VERY_SHALLOW via h/T > 3.0/2.0/1.5); (7) Stores results in RAODatabase (Parquet). sweep_to_dataframe extracts peak RAO per DOF for post-processing. This is the baseline workflow for multi-variant hydrodynamic analysis.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
