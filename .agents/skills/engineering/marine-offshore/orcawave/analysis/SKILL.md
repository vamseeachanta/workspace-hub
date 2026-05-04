---
name: orcawave-analysis
description: Expert agent for OrcaWave diffraction/radiation analysis with deep expertise
  in marine hydrodynamics and panel method computations. Use for wave-structure interaction,
  added mass/damping calculations, QTF computation, and OrcaFlex hydrodynamic database
  generation.
type: reference
version: 1.0.0
updated: 2025-01-02
category: engineering
triggers:
- OrcaWave analysis
- diffraction analysis
- radiation damping
- added mass calculation
- multi-body interaction
- QTF computation
- panel mesh generation
- hydrodynamic database
- wave-structure interaction
- frequency domain analysis
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcawave Analysis

## When to Use

- Diffraction analysis for wave-structure interaction
- Radiation analysis for added mass and damping
- Multi-body hydrodynamic interactions
- QTF (Quadratic Transfer Function) second-order calculations
- Panel mesh generation and optimization
- Batch processing of multiple configurations
- OrcaFlex hydrodynamic database generation
- Frequency domain marine analysis

## Prerequisites

- OrcaWave license (COM API access)
- Python environment with `digitalmodel` package
- Panel mesh geometry files

## Python API

### Basic Analysis

```python
from digitalmodel.orcawave.orcawave_analysis import OrcaWaveAnalysis

# Initialize analysis
orcawave = OrcaWaveAnalysis()

# Configure analysis
config = {
    "vessel_mesh": "geometry/hull_panels.dat",
    "water_depth": 1000.0,

*See sub-skills for full details.*
### Batch Processing

```python
from digitalmodel.orcawave.batch import OrcaWaveBatch

# Initialize batch processor
batch = OrcaWaveBatch(parallel=True, max_workers=4)

# Define configurations
configs = [
    {"name": "draft_full", "draft": 20.0},
    {"name": "draft_ballast", "draft": 12.0},

*See sub-skills for full details.*
### OrcaFlex Integration

```python
from digitalmodel.orcawave.orcaflex_export import OrcaFlexExporter

# Initialize exporter
exporter = OrcaFlexExporter()

# Load OrcaWave results
exporter.load_results("orcawave_results/vessel.dat")

# Export to OrcaFlex hydrodynamic database

*See sub-skills for full details.*
### Mesh Convergence Study

```python
from digitalmodel.orcawave.mesh_study import MeshConvergenceStudy

# Initialize study
study = MeshConvergenceStudy()

# Define mesh sizes to test
mesh_sizes = [2.0, 1.5, 1.0, 0.75, 0.5]

# Run convergence study

*See sub-skills for full details.*

## Related Skills

- [diffraction-analysis](../diffraction-analysis/SKILL.md) - **Master skill** for all diffraction workflows
- [bemrosetta](../bemrosetta/SKILL.md) - AQWA → OrcaFlex conversion with QTF and mesh support
- [orcaflex/modeling](../orcaflex/modeling/SKILL.md) - Apply hydrodynamic database in OrcaFlex
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - AQWA validation and comparison
- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Panel mesh generation
- [hydrodynamics](../hydrodynamics/SKILL.md) - Coefficient management

## References

- Orcina OrcaWave Documentation
- Newman, J.N.: Marine Hydrodynamics
- Faltinsen, O.M.: Sea Loads on Ships and Offshore Structures
- Agent Configuration: `agents/orcawave/agent_config.json`

---

## Version History

- **1.2.0** (2026-02-15): Added production-proven pitfalls (unit traps, result extraction, phase correlation, QTF guard)
- **1.1.0** (2026-01-05): Added AQWA benchmark comparison, peak-focused validation framework, 5% tolerance criteria for significant values
- **1.0.0** (2025-01-02): Initial release from agents/orcawave/ configuration

---

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [Core Capabilities (+2)](core-capabilities/SKILL.md)
- [Performance Targets](performance-targets/SKILL.md)
- [Standard Analysis (+1)](standard-analysis/SKILL.md)
- [Integration Targets](integration-targets/SKILL.md)
- [Workflow Support](workflow-support/SKILL.md)
- [Swarm Coordination (+2)](swarm-coordination/SKILL.md)
- [License Issues (+1)](license-issues/SKILL.md)
- [OrcFxAPI Result Extraction (+3)](orcfxapi-result-extraction/SKILL.md)
- [DiffractionSpec Conventions (spec.yml to OrcaWave)](diffractionspec-conventions-specyml-to-orcawave/SKILL.md)
- [OrcaWave API Properties Reference](orcawave-api-properties-reference/SKILL.md)


## Documentation Reference

llm-wiki base: `data/llm-wiki/orcawave/`

Core theory and data topics:
- `Theory,Governingequations.md` -- BVP formulation for diffraction/radiation
- `Theory,First-orderequations.md` -- first-order panel method equations
- `Theory,Green'sfunction.md` -- Green's function approach
- `Theory,Irregularfrequencies.md` -- irregular frequency removal
- `Data,Bodies.md` -- body definition and mesh assignment
- `Data,Calculationandoutput.md` -- frequency range, output control
- `Results,Addedmassanddamping.md` -- added mass/damping matrix results
- `Results,DisplacementRAOs.md` -- displacement RAO output

Papers (`data/llm-wiki/papers/`):
- `OrcaWave-working-with-meshes.md` -- mesh best practices for OrcaWave
- `Generating-Spectral-RAOs.md` -- spectral RAO generation guidance
