---
title: "Diffraction Analysis System"
tags: [diffraction, hydrodynamics, rao, aqwa, orcawave, bemrosetta, bem, panel-method]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Diffraction Analysis System

Master skill for hydrodynamic diffraction/radiation analysis in the digitalmodel ecosystem. Orchestrates three primary modules (AQWA, OrcaWave, BEMRosetta) and a unified `diffraction` schema layer for cross-solver comparison and data exchange.

## Module Architecture

| Module | Purpose | Primary Use Case |
|--------|---------|------------------|
| **aqwa** | Native AQWA analysis | Direct AQWA .LIS file processing |
| **orcawave** | OrcaWave diffraction | OrcaFlex-integrated analysis |
| **bemrosetta** | Format conversion | AQWA to OrcaFlex workflow, mesh conversion |
| **diffraction** | Unified schemas | Data structures, `DiffractionResults`, comparison framework |

## Workflow Variants

1. **AQWA Analysis Only**: .DAT input, AQWA solver, .LIS parsing, RAO extraction
2. **OrcaWave Analysis**: Panel mesh, OrcaWave solver, OrcaFlex export
3. **Cross-Validation**: Run both solvers, compare RAOs via unified `DiffractionResults` schema
4. **AQWA-to-OrcaFlex Bridge**: BEMRosetta converts AQWA output to OrcaFlex vessel type YAML

## Unit Conversion Traps

These are the most common sources of error in diffraction analysis:

- **OrcaWave frequencies in Hz descending** -- multiply by 2*pi for rad/s, sort ascending for comparison
- **Rotational RAOs in rad/m** -- convert to deg/m for reporting
- **AQWA phase convention (ISO lead)** vs **OrcaWave (Orcina lag)** -- normalize before comparison
- **AQWA QPPL DIFF** required for diffraction (not just QPPL)
- **QTF settings** must NOT be set when QTF is disabled in OrcaWave

## Canonical Output Schema

`DiffractionSpec` YAML format standardizes inputs across solvers. `DiffractionResults` holds RAOs, added mass, damping, and wave excitation forces in a solver-agnostic structure for comparison and downstream consumption.

## Cross-References

- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [BEMRosetta Tool](../entities/bemrosetta-tool.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related concept**: [CFD Offshore Hydrodynamics](../concepts/cfd-offshore-hydrodynamics.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
- **Cross-wiki (marine-engineering)**: [Cathodic Protection System](../../../marine-engineering/wiki/concepts/cathodic-protection-system.md) -- similar slugs (57%); similar titles (57%)
