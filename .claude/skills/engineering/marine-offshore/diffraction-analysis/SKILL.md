---
name: diffraction-analysis
description: Master skill for hydrodynamic diffraction analysis - AQWA, OrcaWave,
  and BEMRosetta integration
version: 1.0.0
updated: 2026-01-27
category: engineering
triggers:
- diffraction analysis
- hydrodynamic analysis
- RAO analysis
- added mass
- radiation damping
- wave forces
- BEM solver
- panel method
- frequency domain
capabilities: []
requires: []
see_also:
- diffraction-analysis-version
- diffraction-analysis-when-to-use-each-module
- diffraction-analysis-diffractionresults-structure
- diffraction-analysis-workflow-1-aqwa-analysis-only
- diffraction-analysis-aqwa-module
- diffraction-analysis-orcaflex-vessel-type-yaml
- diffraction-analysis-coefficient-validation
- diffraction-analysis-required-report-structure-single-page-html
- diffraction-analysis-canonical-specyml-format-diffractionspec
- diffraction-analysis-module-locations
- diffraction-analysis-unit-conversion-traps
tags: []
scripts_exempt: true
---

# Diffraction Analysis

## Overview

This skill provides guidance on hydrodynamic diffraction/radiation analysis using the available modules in digitalmodel. Three primary modules handle different aspects of the workflow:

| Module | Purpose | Primary Use Case |
|--------|---------|------------------|
| **aqwa** | Native AQWA analysis | Direct AQWA .LIS file processing |
| **orcawave** | OrcaWave diffraction | OrcaFlex-integrated analysis |
| **bemrosetta** | Format conversion | AQWA → OrcaFlex workflow, mesh conversion |
| **diffraction** | Unified schemas | Data structures and comparison framework |

## Related Skills

| Skill | Description |
|-------|-------------|
| **aqwa-analysis** | AQWA .LIS processing and RAO extraction |
| **orcawave-analysis** | OrcaWave diffraction/radiation analysis |
| **bemrosetta** | AQWA → OrcaFlex converter with QTF support |
| **hydrodynamics** | 6×6 matrices, wave spectra, OCIMF loading |
| **orcaflex-rao-import** | Multi-format RAO import to OrcaFlex |
| **orcawave-to-orcaflex** | OrcaWave to OrcaFlex conversion |
| **orcawave-aqwa-benchmark** | Cross-validation comparison |

## References

- OrcaFlex Documentation: https://www.orcina.com/webhelp/OrcaFlex/
- WAMIT Manual: https://www.wamit.com/manual.htm
- BEMRosetta: https://github.com/BEMRosetta/BEMRosetta

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version](version/SKILL.md)
- [When to Use Each Module (+1)](when-to-use-each-module/SKILL.md)
- [DiffractionResults Structure](diffractionresults-structure/SKILL.md)
- [Workflow 1: AQWA Analysis Only (+4)](workflow-1-aqwa-analysis-only/SKILL.md)
- [AQWA Module (+2)](aqwa-module/SKILL.md)
- [OrcaFlex Vessel Type YAML (+2)](orcaflex-vessel-type-yaml/SKILL.md)
- [Coefficient Validation (+2)](coefficient-validation/SKILL.md)
- [Required Report Structure (Single-Page HTML) (+3)](required-report-structure-single-page-html/SKILL.md)
- [Canonical spec.yml Format (DiffractionSpec)](canonical-specyml-format-diffractionspec/SKILL.md)
- [Module Locations](module-locations/SKILL.md)
- [Unit Conversion Traps (+3)](unit-conversion-traps/SKILL.md)
