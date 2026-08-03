---
name: crossprovider codex openfoam-cfd-scaling-knee-determined-by-cells-pe
description: OpenFOAM CFD scaling knee determined by cells-per-rank, not total cells
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cfd, openfoam, mpi-scaling, reproducibility]
---

interFoam MPI efficiency degrades when cells-per-rank drops below ~27k (on tested hardware). Scaling does not improve by simply adding more cells to the domain; instead, add both cells and ranks proportionally. Reproducible benchmarks require EXACT version match (e.g., v2312.260127-2).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
