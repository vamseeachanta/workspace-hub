---
name: crossprovider gemini aqwa-solver-requires-dat-format-orcawave-bemrose
description: AQWA solver requires .dat format; OrcaWave/BEMRosetta accept GDF natively
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hydrodynamics, solver-quirks, aqwa, bemrosetta, workflow]
---

AQWA hydrodynamic solver does not accept GeoDF (.gdf) format directly — requires panel mesh (.dat) format. OrcaWave accepts GDF and converts internally; BEMRosetta handles GDF natively. This difference matters when building automated mesh-to-solver pipelines for multi-solver comparison workflows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
