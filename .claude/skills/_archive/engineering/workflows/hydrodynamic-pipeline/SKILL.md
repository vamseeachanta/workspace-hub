---
name: hydrodynamic-pipeline
description: "Cross-program workflow for hydrodynamic analysis \u2014 mesh generation\
  \ (Gmsh) to diffraction analysis (OrcaWave/AQWA) to dynamic analysis (OrcaFlex).\
  \ Covers data flow, format conversion, and validation between programs."
version: 1.0.1
updated: 2026-02-24
category: engineering
triggers:
- hydrodynamic pipeline
- diffraction to dynamic
- OrcaWave to OrcaFlex
- AQWA to OrcaFlex
- panel mesh to RAO
- hydrodynamic workflow
- wave-structure interaction pipeline
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires:
- gmsh-meshing
- orcawave-analysis
- orcaflex-modeling
see_also:
- hydrodynamic-pipeline-pipeline-overview
- hydrodynamic-pipeline-gmsh-panel-mesh-for-hydrodynamics
- hydrodynamic-pipeline-orcawave-execution
- hydrodynamic-pipeline-orcawave-to-orcaflex-direct-integration
- hydrodynamic-pipeline-orcaflex-model-assembly
- hydrodynamic-pipeline-checkpoint-1-mesh-quality
- hydrodynamic-pipeline-error-propagation-where-things-break
tags: []
scripts_exempt: true
---

# Hydrodynamic Pipeline

## Related Skills

- [orcawave-analysis](../../marine-offshore/orcawave-analysis/SKILL.md) - OrcaWave diffraction
- [orcawave-to-orcaflex](../../marine-offshore/orcawave-to-orcaflex/SKILL.md) - OrcaWave→OrcaFlex conversion
- [aqwa-analysis](../../marine-offshore/aqwa-analysis/SKILL.md) - AQWA diffraction
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) - OrcaFlex dynamic analysis
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Panel mesh generation
- [bemrosetta](../../marine-offshore/bemrosetta/SKILL.md) - Format conversion

---

## Version History

- **1.0.1** (2026-02-24): Fixed OrcaWave result extraction — use VesselType not Vessel for diffraction data (validated 73/74→74/74)
- **1.0.0** (2026-02-23): Initial cross-program workflow skill for hydrodynamic pipeline (WRK-372 Phase 4).

## Sub-Skills

- [Pipeline Overview](pipeline-overview/SKILL.md)
- [Gmsh Panel Mesh for Hydrodynamics (+3)](gmsh-panel-mesh-for-hydrodynamics/SKILL.md)
- [OrcaWave Execution (+3)](orcawave-execution/SKILL.md)
- [OrcaWave to OrcaFlex (Direct Integration) (+3)](orcawave-to-orcaflex-direct-integration/SKILL.md)
- [OrcaFlex Model Assembly (+1)](orcaflex-model-assembly/SKILL.md)
- [Checkpoint 1: Mesh Quality (+2)](checkpoint-1-mesh-quality/SKILL.md)
- [Error Propagation: Where Things Break](error-propagation-where-things-break/SKILL.md)
