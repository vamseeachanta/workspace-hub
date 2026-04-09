---
title: "AQWA Solver"
tags: [aqwa, ansys, diffraction, hydrodynamics, dat-format, lis-parsing]
sources:
  - dark-intelligence-extractions
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# AQWA Solver

ANSYS AQWA is a hydrodynamic diffraction and radiation solver for floating and fixed offshore structures. It computes wave loads, RAOs, added mass, radiation damping, and drift forces using panel methods. In the workspace-hub ecosystem, AQWA runs on the licensed Windows machine and is accessed via DAT input files and LIS output parsing.

## Executable and Invocation

```
$AQWA_HOME/bin/winx64/Aqwa.exe
```

- Input: DAT file (structured keyword format)
- Output: LIS file (text-based results), plus binary restart files

## Critical Configuration Rules

### Element Types

Elements **must** use `QPPL DIFF` (not just `QPPL`) for diffraction analysis. Using `QPPL` alone runs only Morison-type hydrodynamics — no panel diffraction, no RAOs.

### OPTIONS GOON

The `OPTIONS GOON` directive tells AQWA to continue past non-fatal errors. However:

- It does **NOT** override mesh FATAL errors
- Mesh FATALs (e.g., overlapping panels, non-watertight hull) require fixing the mesh directly
- There is no workaround — fix the geometry, re-mesh, and resubmit

## DAT File Format

Key sections in an AQWA DAT input file:

| Section | Purpose |
|---------|---------|
| `DECK` | Title and administrative data |
| `NODE` | Node coordinates for panel mesh |
| `ELEM` | Element connectivity (quad panels) |
| `QPPL DIFF` | Marks elements for diffraction analysis |
| `MASS` | Mass and inertia properties |
| `FREQUENCY` | Wave frequency list (rad/s) |
| `HEADING` | Wave direction list (degrees) |
| `OPTIONS GOON` | Continue past non-fatal errors |

## LIS File Parsing

The LIS output file contains results in formatted text blocks. Key parsing rules:

1. **Normalize whitespace before keyword matching** — AQWA output contains inconsistent spacing. For example, `"ADDED  MASS"` has a double space between words. Always collapse multiple spaces before matching keywords.
2. **Frequency order**: Results are in the order specified in the DAT file, typically ascending rad/s.
3. **Unit system**: Frequencies in **rad/s**, forces in N or kN depending on model units.
4. **RAO array shape**: Verify dimensions match `(nheading, nfreq, 6)` — shape and transpose errors are common when comparing across solvers.

## Comparison with OrcaFlex

| Property | AQWA | OrcaFlex/OrcaWave |
|----------|------|-------------------|
| Frequency unit | rad/s | Hz |
| Frequency order | Ascending (typically) | Descending |
| Rotational RAOs | Check per model | radians/m |
| Input format | DAT text file | .dat / .yml binary |
| Output format | LIS text file | OrcFxAPI objects |

## Cross-References

- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [BEMRosetta Tool](../entities/bemrosetta-tool.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
- **Cross-wiki (naval-architecture)**: [Seakeeping and Ship Motions](../../../naval-architecture/wiki/concepts/seakeeping.md) — AQWA computes vessel RAOs and motion responses used in seakeeping assessment
- **Cross-wiki (naval-architecture)**: [Ship Hydrostatics](../../../naval-architecture/wiki/concepts/hydrostatics.md) — AQWA uses hydrostatic properties (displacement, waterplane area) as fundamental inputs
