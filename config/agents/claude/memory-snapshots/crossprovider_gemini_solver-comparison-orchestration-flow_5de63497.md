---
name: crossprovider gemini solver-comparison-orchestration-flow
description: Solver comparison orchestration flow
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [solver-benchmarking, orchestration, hydrodynamics]
---

Multi-solver benchmarking follows: BenchmarkConfig → pre-computed DiffractionResults per solver → MultiSolverComparator (produces BenchmarkReport) → BenchmarkPlotter (generates plots) → JSON export → HTML report generation. Optional per-solver metadata dict attaches input geometry/mesh info to comparison table.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
