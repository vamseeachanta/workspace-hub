---
name: orcawave-damping-sweep
description: Viscous damping analysis for OrcaWave. Use when running parametric damping
  sweeps, optimizing roll damping coefficients, computing critical damping, or comparing
  damping results with model test data for vessel motion tuning.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- damping sweep
- roll damping
- viscous damping study
- critical damping
- damping optimization
- bilge keel effect
- damping coefficient tuning
- model test comparison
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcawave Damping Sweep

## When to Use

- Parametric studies of viscous damping effects
- Roll damping coefficient optimization
- Comparing radiation damping with viscous damping
- Tuning damping to match model test data
- Estimating bilge keel damping contribution
- Critical damping ratio calculations
- Sensitivity analysis for motion predictions
- Roll resonance mitigation studies

## Python API

### Basic Damping Sweep

```python
from digitalmodel.orcawave.damping import DampingSweep

# Initialize sweep
sweep = DampingSweep()

# Load base model
sweep.load_model("models/fpso.owr")

# Define damping values to sweep

*See sub-skills for full details.*
### Multi-Parameter Sweep

```python
from digitalmodel.orcawave.damping import MultiParameterDampingSweep

# Initialize multi-parameter sweep
sweep = MultiParameterDampingSweep()

# Load model
sweep.load_model("models/fpso.owr")

# Define parameter space

*See sub-skills for full details.*
### Critical Damping Calculation

```python
from digitalmodel.orcawave.damping import CriticalDampingCalculator

# Initialize calculator
calc = CriticalDampingCalculator()

# Load model with mass and stiffness
calc.load_model("models/fpso.owr")

# Calculate critical damping for each DOF

*See sub-skills for full details.*
### Model Test Comparison

```python
from digitalmodel.orcawave.damping import ModelTestComparison

# Initialize comparison
comparison = ModelTestComparison()

# Load OrcaWave results
comparison.load_orcawave_results("results/fpso.owr")

# Load model test data

*See sub-skills for full details.*
### Bilge Keel Estimation

```python
from digitalmodel.orcawave.damping import BilgeKeelDamping

# Initialize bilge keel damping estimator
bk = BilgeKeelDamping()

# Configure vessel parameters
bk.configure_vessel(
    beam=50.0,          # m
    draft=22.0,         # m

*See sub-skills for full details.*
### Damping-Period Relationship

```python
from digitalmodel.orcawave.damping import DampingPeriodAnalyzer

# Analyze damping vs period relationship
analyzer = DampingPeriodAnalyzer()

# Load OrcaWave radiation damping results
analyzer.load_results("models/fpso.owr")

# Extract frequency-dependent radiation damping

*See sub-skills for full details.*

## Related Skills

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - OrcaWave diffraction analysis
- [orcawave-to-orcaflex](../orcawave-to-orcaflex/SKILL.md) - Export with damping
- [hydrodynamics](../hydrodynamics/SKILL.md) - Coefficient management
- [viv-analysis](../viv-analysis/SKILL.md) - Vibration damping

## References

- Himeno, Y.: Prediction of Ship Roll Damping - State of the Art
- Ikeda, Y.: Prediction Methods of Roll Damping of Ships
- OrcaWave Roll Damping Documentation
- Script: `scripts/python/digitalmodel/modules/run_orcawave_damping_sweep.py`

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with damping sweep, model test comparison, and bilge keel estimation

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Total Damping Composition (+1)](total-damping-composition/SKILL.md)
- [Damping Sweep Configuration (+1)](damping-sweep-configuration/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Typical Values by Vessel Type (+1)](typical-values-by-vessel-type/SKILL.md)
- [Damping-Related Properties](damping-related-properties/SKILL.md)


## Documentation Reference

OrcaWave topics (`data/llm-wiki/orcawave/`):
- `Theory,Dampinglid.md` -- damping lid method for free-surface suppression
- `Theory,Hydrodynamicdrag.md` -- linearized viscous drag in frequency domain
- `Results,Rolldamping.md` -- roll damping results output
- `Results,Addedmassanddamping.md` -- radiation damping vs frequency
- `Data,Springdampers.md` -- external damping specification

OrcaFlex topics (`data/llm-wiki/orcaflex/`):
- `Vesseltypes,Otherdamping.md` -- additional damping in vessel types
- `Vesseltheory,Otherdamping.md` -- damping theory beyond radiation

Papers (`data/llm-wiki/papers/`):
- `Structural-Damping.md` -- structural damping concepts
- `Spar-Buoy-Equation-of-Motion.md` -- damping in spar buoy dynamics
