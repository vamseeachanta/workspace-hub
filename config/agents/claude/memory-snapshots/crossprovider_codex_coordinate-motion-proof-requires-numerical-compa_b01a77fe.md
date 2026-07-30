---
name: crossprovider codex coordinate-motion-proof-requires-numerical-compa
description: Coordinate motion proof requires numerical comparison, not digest or header comparison
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [openfoam, mesh, motion-proof, mpi]
---

OpenFOAM points files include time-relative headers that differ even when coordinates are identical. Hash/digest comparison proves the file changed, not that coordinates moved. Parse the binary payload and compare numerically per-processor or after explicit reconstruction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
