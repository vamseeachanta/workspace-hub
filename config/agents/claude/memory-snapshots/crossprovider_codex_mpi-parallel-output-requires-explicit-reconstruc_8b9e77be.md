---
name: crossprovider codex mpi-parallel-output-requires-explicit-reconstruc
description: MPI parallel output requires explicit reconstruction before comparison
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [mpi, openfoam, verification]
---

When MPI solver output distributes across processor trees, comparing digests of deleted processor trees proves nothing. Add explicit reconstruction stage or parse in-place per processor before asserting motion or completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
