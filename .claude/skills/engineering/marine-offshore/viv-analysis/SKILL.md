---
name: viv-analysis
description: Assess vortex-induced vibration (VIV) for risers and tubular members
  with natural frequency and safety factor calculations. Use for VIV susceptibility
  analysis, natural frequency calculation, vortex shedding assessment, and tubular
  member fatigue from VIV.
updated: '2026-01-07'
capabilities: []
requires: []
see_also:
- viv-analysis-version-metadata
- viv-analysis-100-2026-01-07
- viv-analysis-1-natural-frequency-analysis
- viv-analysis-strouhal-number
- viv-analysis-complete-viv-screening-workflow
- viv-analysis-natural-frequencies-json
- viv-analysis-design-code-references
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

# Viv Analysis

## When to Use

- VIV analysis for risers and pipelines
- Natural frequency calculation for tubular members
- Vortex shedding frequency analysis
- VIV fatigue damage assessment
- Tubular member VIV screening
- Safety factor evaluation against VIV criteria

## Prerequisites

- Python environment with `digitalmodel` package installed
- Member geometry and material properties
- Current velocity profiles
- For risers: tension distribution along length

## Python API

### Natural Frequency Calculation

```python
from digitalmodel.subsea.viv_analysis.viv_analysis import VIVAnalysis
from digitalmodel.subsea.viv_analysis.viv_tubular_members import VIVTubularMembers

# Initialize analysis
viv = VIVAnalysis()

# Define member properties
member = {
    "length": 50.0,

*See sub-skills for full details.*
### Vortex Shedding Analysis

```python
# Vortex shedding frequency
diameter = 0.5  # meters
current_velocity = 1.5  # m/s
strouhal = 0.2

shedding_freq = viv.vortex_shedding_frequency(
    diameter=diameter,
    velocity=current_velocity,
    strouhal_number=strouhal

*See sub-skills for full details.*
### Tubular Member Analysis

```python
from digitalmodel.subsea.viv_analysis.viv_tubular_members import VIVTubularMembers

# Initialize tubular member analysis
tubular = VIVTubularMembers()

# Define member
member_props = {
    "name": "Brace1",
    "outer_diameter": 0.324,

*See sub-skills for full details.*
### VIV Fatigue Assessment

```python
from digitalmodel.subsea.viv_analysis.viv_fatigue import VIVFatigue

# Initialize VIV fatigue analysis
viv_fatigue = VIVFatigue()

# Calculate VIV-induced stress range
stress_range = viv_fatigue.calculate_stress_range(
    amplitude=0.5,  # VIV amplitude in diameters
    diameter=0.324,

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `VIVAnalysis` | Main VIV analysis router |
| `VIVTubularMembers` | Tubular member assessment |
| `VIVAnalysisComponents` | Component-level analysis |
| `VIVFatigue` | VIV-induced fatigue damage |

## Related Skills

- [catenary-riser](../catenary-riser/SKILL.md) - Riser configuration
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - VIV fatigue damage
- [structural-analysis](../structural-analysis/SKILL.md) - Stress verification

## References

- DNV-RP-C205: Environmental Conditions and Environmental Loads
- DNV-RP-F105: Free Spanning Pipelines
- Blevins, R.D.: Flow-Induced Vibration

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [1. Natural Frequency Analysis (+3)](1-natural-frequency-analysis/SKILL.md)
- [Strouhal Number (+2)](strouhal-number/SKILL.md)
- [Complete VIV Screening Workflow](complete-viv-screening-workflow/SKILL.md)
- [Natural Frequencies JSON (+1)](natural-frequencies-json/SKILL.md)
- [Design Code References](design-code-references/SKILL.md)
