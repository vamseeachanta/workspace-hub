---
name: crossprovider codex file-digest-changes-do-not-prove-mesh-coordinate
description: File digest changes do not prove mesh/coordinate motion in OpenFOAM
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [openfoam, mesh, correctness, motion-proof, parallelism]
---

OpenFOAM IOobject headers include time-relative location metadata, so raw file digests differ between time steps even when coordinates are unchanged. Motion proof requires explicit numerical coordinate comparison (parse payload, not just hash) or reconstruction of parallel-processor output before comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
