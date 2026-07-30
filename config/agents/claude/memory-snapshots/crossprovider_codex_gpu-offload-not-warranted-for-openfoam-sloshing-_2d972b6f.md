---
name: crossprovider codex gpu-offload-not-warranted-for-openfoam-sloshing-
description: GPU offload not warranted for OpenFOAM sloshing CFD
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [cfd, openfoam, gpu, performance]
---

VOF/MULES/PIMPLE dominate the compute profile; no PETSc/AmgX/petsc4Foam bridge exists. CPU/MPI at 8 ranks remains the optimal lane for tank sloshing interFoam simulations (0.5899 s/step @ 216k cells is the reference).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
