---
name: crossprovider codex openfoam-workflow-audit-uses-six-phase-structure
description: OpenFOAM workflow audit uses six-phase structure: problem/setup/mesh/exec/post/report, distinguishing planning estimates from benchmarked values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [openfoam, cfd, methodology, workflow, planning, benchmarking]
---

Formal auditable CFD recommendation structure applies problem definition and mesh-count/runtime planning estimates explicitly labeled as estimates, not benchmarks. Distinguish: published benchmark counts from this case's predicted counts (e.g., peak bytes/cell RAM-gating on an 8-vCPU/62-GiB node). Medium/fine GCI and IDDES work route to burst HPC; local meshes stay RAM-constrained.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
