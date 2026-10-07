---
name: viv-analysis
description: Assess vortex-induced vibration (VIV) for risers and tubular members
  with natural frequency and safety factor calculations. Use for VIV susceptibility
  analysis, natural frequency calculation, vortex shedding assessment, and tubular
  member fatigue from VIV.
type: reference
updated: '2026-01-07'
capabilities: []
requires: []
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

<!-- ace:api-missing-warning -->
> [!WARNING]
> **Part of the Python API documented below does not exist in
> `digitalmodel`.** These snippets are a *specification* of intended
> capability, not runnable code. Do not import them, and do not report
> a result obtained by pretending they ran.
>
> Absent as of this revision:
>   - `digitalmodel.subsea.viv_analysis.viv_fatigue`
>   - `digitalmodel.subsea.viv_analysis.viv_fatigue.VIVFatigue`
>
> The surrounding engineering content — method, conventions, what to
> watch for — is unaffected and remains usable. Tracked in
> aceengineer-strategy#267.

<!-- ace:known-missing: digitalmodel.subsea.viv_analysis.viv_fatigue, digitalmodel.subsea.viv_analysis.viv_fatigue.VIVFatigue -->

# Viv Analysis

## When to Use

- VIV analysis for risers and pipelines
- Pipeline free-span VIV screening and fatigue prechecks
- Natural frequency calculation for tubular members
- Vortex shedding frequency analysis
- VIV fatigue damage assessment
- Tubular member VIV screening
- Safety factor evaluation against VIV criteria
- Pressure wall prechecks when VIV span inputs depend on pipe wall/section properties

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

## Pipeline Free-Span VIV Workflow Notes

For subsea pipeline span work, treat VIV screening as a coupled structural/fatigue workflow rather than a standalone vortex-shedding calculation:

1. Establish pipe section properties from the actual design basis: OD, nominal WT, corrosion allowance, mill tolerance, grade/SMYS, weld factor, temperature factor, and code/design factor.
2. Run a pressure-wall sanity check before relying on the section for span/fatigue calculations. When using `digitalmodel`, prefer the pipe-capacity implementation under `src/digitalmodel/structural/pipe_capacity/` and document the equation branch used.
3. Use minimum/corroded wall for span stress and fatigue section properties unless the governing code or project basis specifies another convention.
4. Then evaluate span natural frequencies, reduced velocity, lock-in susceptibility, stress range, fatigue damage, and acceptance criteria under DNV-RP-F105 / DNV-ST-F101 or project-specific rules.
5. Do not present pressure containment as final wall adequacy; collapse, propagation buckling, local buckling, installation, hydrotest, thermal/strain, on-bottom stability, and VIV/free-span fatigue may still govern.

See `references/pipeline-span-pressure-wall-precheck.md` for the session-derived digitalmodel pressure-wall pattern and 12 in / 3000 psi example.

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
