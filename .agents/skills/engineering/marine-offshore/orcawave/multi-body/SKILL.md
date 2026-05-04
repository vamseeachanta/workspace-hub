---
name: orcawave-multi-body
description: Multi-body hydrodynamic interaction analysis in OrcaWave. Use when setting
  up coupled vessel models, side-by-side operations, FPSO-tanker interactions, gap
  resonance studies, or hydrodynamic shielding calculations.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- multi-body hydrodynamics
- side-by-side operation
- coupled vessel analysis
- FPSO tanker interaction
- gap resonance
- hydrodynamic shielding
- STS transfer
- offloading operation
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcawave Multi Body

## When to Use

- Side-by-side (STS) ship-to-ship transfer operations
- FPSO and offloading tanker interaction
- Multiple floating bodies in close proximity
- Gap resonance phenomenon investigation
- Hydrodynamic shielding effects
- Coupled vessel response analysis
- Multi-body mooring system design

## Python API

### Basic Multi-Body Setup

```python
from digitalmodel.orcawave.multibody import MultiBodyAnalysis

# Initialize multi-body analysis
mb = MultiBodyAnalysis()

# Add primary vessel (FPSO)
mb.add_body(
    name="FPSO",
    mesh_file="geometry/fpso_panels.gdf",

*See sub-skills for full details.*
### Gap Resonance Analysis

```python
from digitalmodel.orcawave.multibody import GapResonanceAnalyzer

# Initialize gap resonance analyzer
gap = GapResonanceAnalyzer()

# Configure gap geometry
gap.configure(
    vessel1="FPSO",
    vessel2="Shuttle_Tanker",

*See sub-skills for full details.*
### Side-by-Side Operations

```python
from digitalmodel.orcawave.multibody import SideBySideAnalysis

# Initialize STS analysis
sts = SideBySideAnalysis()

# Configure vessels
sts.configure_fpso(
    mesh="geometry/fpso.gdf",
    loa=300.0,

*See sub-skills for full details.*
### Hydrodynamic Coupling Matrices

```python
from digitalmodel.orcawave.multibody import CouplingMatrixExtractor

# Extract coupling matrices
extractor = CouplingMatrixExtractor()

# Load multi-body results
extractor.load_results("results/multibody.owr")

# Get coupled added mass (12x12 for 2 bodies)

*See sub-skills for full details.*
### Shielding Effects

```python
from digitalmodel.orcawave.multibody import ShieldingAnalyzer

# Analyze wave shielding
shielding = ShieldingAnalyzer()

# Configure
shielding.load_multibody_results("results/multibody.owr")

# Compare sheltered vs exposed

*See sub-skills for full details.*

## Related Skills

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - Single body diffraction
- [orcawave-mesh-generation](../orcawave-mesh-generation/SKILL.md) - Panel mesh creation
- [orcawave-to-orcaflex](../orcawave-to-orcaflex/SKILL.md) - Export to OrcaFlex
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design

## References

- Faltinsen, O.M.: Sea Loads on Ships and Offshore Structures
- Newman, J.N.: Wave Effects on Deformable Bodies
- Molin, B.: On the Piston and Sloshing Modes in Moonpools
- OrcaWave Multi-Body Documentation

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with STS analysis, gap resonance, and coupling matrix extraction

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Common Scenarios (+1)](common-scenarios/SKILL.md)
- [Multi-Body Analysis Configuration (+1)](multi-body-analysis-configuration/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Export for Time-Domain](export-for-time-domain/SKILL.md)


## Documentation Reference

OrcaWave topics (`data/llm-wiki/orcawave/`):
- `Data,Bodies.md` -- multi-body definition (multiple bodies per model)
- `Data,Constraints.md` -- inter-body constraints
- `Data,Springdampers.md` -- external stiffness/damping between bodies
- `Theory,Dampinglid.md` -- damping lid for gap resonance suppression
- `Results,Addedmassanddamping.md` -- coupled AMD matrices (NxN body DOFs)
- `Data,Calculationandoutput.md` -- multi-body output control

OrcaFlex topics (`data/llm-wiki/orcaflex/`):
- `Vesseltypes,Multibodydata.md` -- multi-body vessel type data in OrcaFlex
- `Vesseltheory,Impulseresponseandconvolution.md` -- coupled time-domain approach

Papers (`data/llm-wiki/papers/`):
- `Buoy-Vessel-Modelling.md` -- buoy-vessel interaction modelling
