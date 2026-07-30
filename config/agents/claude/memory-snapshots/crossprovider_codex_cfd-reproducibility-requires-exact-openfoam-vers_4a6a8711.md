---
name: crossprovider codex cfd-reproducibility-requires-exact-openfoam-vers
description: CFD reproducibility requires exact OpenFOAM version and mesh pinning
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cfd, reproducibility, performance]
---

OpenFOAM benchmark wall-clock times vary with build version (e.g., v2312 build 2312.260127-2) and mesh size. Reproducible cross-machine comparisons require identical OpenFOAM builds and cell counts; MPI scaling benchmarks are sensitive to cells-per-rank ratios (~27k/rank is a knee for contention).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
