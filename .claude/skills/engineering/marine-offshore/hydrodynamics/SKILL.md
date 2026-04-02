---
name: hydrodynamics
description: "Manage hydrodynamic coefficients, wave spectra, and environmental loading\
  \ for vessel response analysis. Use for 6\xD76 matrix management, wave spectrum\
  \ modeling, OCIMF loading calculations, and RAO interpolation."
type: reference
updated: '2026-01-07'
capabilities: []
requires: []
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

# Hydrodynamics

## When to Use

- 6×6 added mass and damping matrix management
- Wave spectrum modeling (JONSWAP, Bretschneider, PM)
- OCIMF wind and current loading calculations
- RAO interpolation and frequency-dependent coefficients
- Hydrodynamic coefficient database management
- Kramers-Kronig causality validation

## Prerequisites

- Python environment with `digitalmodel` package installed
- Hydrodynamic coefficient data (from AQWA, WAMIT, etc.)
- Environmental data for wave/wind/current loading

## Python API

### Coefficient Database

```python
from digitalmodel.hydrodynamics.coefficient_database import CoefficientDatabase

# Initialize database
db = CoefficientDatabase()

# Store coefficients
db.store(
    vessel_name="FPSO",
    frequency=0.1,

*See sub-skills for full details.*
### Frequency-Dependent Matrices

```python
from digitalmodel.hydrodynamics.freq_dependent import FrequencyDependentMatrix

# Initialize with frequency-dependent data
fdm = FrequencyDependentMatrix()
fdm.load("hydro_data.json")

# Interpolate to specific frequency
A_interp = fdm.interpolate_added_mass(frequency=0.15)
B_interp = fdm.interpolate_damping(frequency=0.15)

# Get infinite frequency added mass
A_inf = fdm.get_infinite_frequency_added_mass()
```
### Wave Spectra

```python
from digitalmodel.hydrodynamics.wave_spectra import WaveSpectra

# Create JONSWAP spectrum
spectrum = WaveSpectra()
frequencies, S = spectrum.jonswap(
    hs=3.5,       # Significant wave height (m)
    tp=10.0,      # Peak period (s)
    gamma=3.3,    # Peakedness parameter
    freq_min=0.02,

*See sub-skills for full details.*
### OCIMF Loading

```python
from digitalmodel.hydrodynamics.ocimf_loading import OCIMFLoading

# Initialize calculator
ocimf = OCIMFLoading()

# Define vessel
vessel = {
    "length": 300.0,
    "beam": 50.0,

*See sub-skills for full details.*
### Coefficient Interpolation

```python
from digitalmodel.hydrodynamics.interpolator import CoefficientsInterpolator

# Initialize interpolator
interp = CoefficientsInterpolator()

# Load RAO data
interp.load_raos("vessel_raos.csv")

# Interpolate to new frequencies

*See sub-skills for full details.*
### Causality Validation

```python
from digitalmodel.hydrodynamics.validation import HydroValidator

# Initialize validator
validator = HydroValidator()

# Load frequency-dependent coefficients
validator.load_coefficients("hydro_data.json")

# Kramers-Kronig check

*See sub-skills for full details.*
### Displacement RAO Quality Checks

```python
import yaml
from digitalmodel.marine_ops.marine_analysis import (
    RAODataValidators,
    VesselType,
    DisplacementRAOQualityReport
)
from digitalmodel.marine_ops.marine_analysis.rao_quality_report import RAOQualityReportGenerator

# Load OrcaFlex RAO data

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `CoefficientDatabase` | Coefficient storage and retrieval |
| `FrequencyDependentMatrix` | 6×6 matrix interpolation |
| `WaveSpectra` | Spectrum generation (JONSWAP, PM, etc.) |
| `OCIMFLoading` | OCIMF wind/current calculations |
| `CoefficientsInterpolator` | 2D interpolation (freq × direction) |
| `HydroValidator` | Kramers-Kronig and matrix validation |
| `RAODataValidators` | RAO quality checks (phase, peaks, vessel type) |
| `RAOQualityReportGenerator` | HTML/CSV quality report generation |

## Related Skills

- [diffraction-analysis](../diffraction-analysis/SKILL.md) - **Master skill** for all diffraction workflows
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - Extract coefficients from AQWA
- [bemrosetta](../bemrosetta/SKILL.md) - AQWA → OrcaFlex conversion with QTF and mesh support
- [orcaflex/modeling](../orcaflex/modeling/SKILL.md) - Apply in OrcaFlex models
- [viv-analysis](../viv-analysis/SKILL.md) - Hydrodynamic coefficient usage

## References

- DNV-RP-C205: Environmental Conditions and Environmental Loads
- OCIMF: Mooring Equipment Guidelines
- Newman, J.N.: Marine Hydrodynamics

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [1. Coefficient Database Management (+4)](1-coefficient-database-management/SKILL.md)
- [Wave Spectrum Types](wave-spectrum-types/SKILL.md)
- [Coefficient Database JSON (+1)](coefficient-database-json/SKILL.md)
