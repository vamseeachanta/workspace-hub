---
name: crossprovider codex cfd-reproducibility-precise-openfoam-versioning-
description: CFD reproducibility: precise OpenFOAM versioning and baseline tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [cfd, reproducibility, benchmarking, versioning]
---

When benchmarking CFD (e.g. interFoam scaling) across machines, pin OpenFOAM version exactly (e.g. 2312.260127-2, not just 2312.x) and commit baseline manifests (e.g. sloshing-3d-benchmark.json) to repo. Track cells/rank as a key scaling knee metric; cores alone don't predict performance under contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
