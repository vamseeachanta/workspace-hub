---
name: orcawave-qtf-analysis
description: Second-order wave force QTF computation in OrcaWave. Use when computing
  mean drift forces, difference-frequency or sum-frequency QTFs, slow-drift response,
  or applying Newman approximation for offshore structures.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- QTF computation
- quadratic transfer function
- mean drift force
- second order wave forces
- difference frequency
- sum frequency
- slow drift
- Newman approximation
- full QTF
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcawave Qtf Analysis

## When to Use

- Computing mean drift forces for mooring analysis
- Generating full QTF matrices for slow-drift response
- Difference-frequency force calculation
- Sum-frequency force calculation (springing)
- Newman approximation vs full QTF comparison
- Deep water vs shallow water second-order effects
- Moored vessel slow-drift motion prediction

## Python API

### Basic QTF Computation

```python
from digitalmodel.orcawave.qtf import OrcaWaveQTF

# Initialize QTF analysis
qtf = OrcaWaveQTF()

# Load OrcaWave model with first-order results
qtf.load_model("models/fpso.owr")

# Configure QTF computation

*See sub-skills for full details.*
### Full QTF Matrix Generation

```python
from digitalmodel.orcawave.qtf import FullQTFComputation

# Initialize full QTF computation
full_qtf = FullQTFComputation()

# Configure frequency pairs
full_qtf.configure(
    frequencies=np.linspace(0.02, 0.5, 25),  # rad/s
    heading_pairs=[

*See sub-skills for full details.*
### Newman Approximation

```python
from digitalmodel.orcawave.qtf import NewmanApproximation

# Initialize Newman approximation
newman = NewmanApproximation()

# Load first-order results
newman.load_first_order_results("results/fpso_raos.csv")

# Compute approximate QTF

*See sub-skills for full details.*
### Mean Drift Analysis

```python
from digitalmodel.orcawave.qtf import MeanDriftAnalyzer

# Initialize analyzer
drift = MeanDriftAnalyzer()

# Load OrcaWave results
drift.load_results("models/fpso.owr")

# Extract mean drift by method

*See sub-skills for full details.*
### Slow Drift Response

```python
from digitalmodel.orcawave.qtf import SlowDriftResponse

# Initialize slow drift analysis
slow_drift = SlowDriftResponse()

# Load QTF data
slow_drift.load_qtf("results/fpso_qtf.yml")

# Configure sea state

*See sub-skills for full details.*

## Related Skills

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - First-order diffraction analysis
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design
- [hydrodynamics](../hydrodynamics/SKILL.md) - Wave loading management
- [orcaflex/modeling](../orcaflex/modeling/SKILL.md) - Time-domain simulation

## References

- Pinkster, J.A.: Low Frequency Second Order Wave Exciting Forces
- Newman, J.N.: Second-Order Wave Forces on a Vertical Cylinder
- Standing, R.G.: Low Frequency Wave Drift Forces
- OrcaWave QTF Documentation

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with full QTF, Newman approximation, and slow drift analysis

## Sub-Skills

- [When to Use Full QTF vs Newman (+2)](when-to-use-full-qtf-vs-newman/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Force Components (+1)](force-components/SKILL.md)
- [QTF Analysis Configuration (+1)](qtf-analysis-configuration/SKILL.md)
- [Available Data (+1)](available-data/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)


## Documentation Reference

OrcaWave topics (`data/llm-wiki/orcawave/`):
- `Data,QTFs.md` -- QTF computation configuration
- `Theory,Second-orderequations.md` -- second-order BVP theory
- `Results,Quadraticloads.md` -- QTF output (mean drift, full QTF matrices)
- `Results,Potentialloads.md` -- potential-based load results
- `Data,Environment.md` -- water depth affecting second-order effects

OrcaFlex topics (`data/llm-wiki/orcaflex/`):
- `Vesseltypes,WavedriftandsumfrequencyQTFs.md` -- QTF data in vessel types
- `Vesseltheory,Wavedriftandsumfrequencyloads.md` -- drift/sum-frequency theory
- `Modellingvesselslowdrift.md` -- slow drift modelling in OrcaFlex
