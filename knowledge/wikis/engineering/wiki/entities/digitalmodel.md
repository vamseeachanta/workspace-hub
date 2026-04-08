---
title: "digitalmodel"
tags: [repository, engineering, python, packages, calculations]
sources:
  - digitalmodel-architecture-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# digitalmodel

The core engineering Python repository. A separate git repo (submodule of workspace-hub) containing 30 packages, 1587 Python files, 2085 classes, and 1956 functions.

## Top Packages (by file count)

| Package | Files | Classes | Functions | Has Tests |
|---------|------:|--------:|----------:|:---------:|
| solvers | 309 | 477 | 254 | Yes |
| structural | 191 | 249 | 264 | Yes |
| hydrodynamics | 173 | 291 | 382 | Yes |
| infrastructure | 165 | 141 | 96 | Yes |
| marine_ops | 117 | 210 | 177 | Yes |
| workflows | 92 | 179 | 68 | Yes |
| subsea | 65 | 76 | 129 | Yes |
| data_systems | 58 | 50 | 33 | Yes |

## Key Domains

- **OrcaFlex** -- marine dynamic analysis modeling
- **Hydrodynamics** -- AQWA, OrcaWave, diffraction analysis
- **Structural** -- FEA, fitness-for-service, API 579
- **Cathodic protection** -- CP design per DNV-RP-B401
- **Subsea** -- pipeline, riser, umbilical engineering

## Development Rules

- Separate git repo -- `cd digitalmodel/` before committing
- Tests required for 24/30 packages
- `uv run` for all Python execution

## Cross-References

- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related concept**: [[test-driven-development]]
- **Domain wiki**: [Marine Engineering](../../../../marine-engineering/wiki/index.md)
