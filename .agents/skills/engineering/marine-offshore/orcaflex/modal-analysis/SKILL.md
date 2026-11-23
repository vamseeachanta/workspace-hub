---
name: orcaflex-modal-analysis
description: Perform modal and frequency analysis on OrcaFlex models to extract natural
  frequencies, mode shapes, and identify dominant DOF responses. Use for VIV assessment,
  resonance identification, and structural dynamics characterization.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- modal analysis
- natural frequency
- mode shapes
- frequency analysis
- eigenvalue analysis
- resonance identification
- DOF analysis
- structural dynamics
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Modal Analysis

## When to Use

- Extract natural frequencies from OrcaFlex models
- Calculate mode shapes for risers, lines, and structures
- Identify dominant degrees of freedom in each mode
- Filter modes by specific DOF (heave, surge, pitch, etc.)
- VIV susceptibility screening (compare natural frequencies to shedding frequencies)
- Resonance identification for environmental loading
- Batch processing multiple water depths or configurations

## Prerequisites

- OrcaFlex license (for OrcFxAPI)
- Python environment with `digitalmodel` package installed
- Model files (.dat, .yml, or .sim)

## Python API

### Basic Modal Analysis

```python
from digitalmodel.orcaflex.orcaflex_modal_analysis import OrcModalAnalysis

# Initialize analyzer
modal = OrcModalAnalysis()

# Configure analysis
cfg = {
    "default": {
        "Analysis": {

*See sub-skills for full details.*
### Direct OrcFxAPI Usage

```python
import OrcFxAPI

# Load model and calculate statics
model = OrcFxAPI.Model()
model.LoadData("model.yml")
model.CalculateStatics()

# Configure modal analysis
spec = OrcFxAPI.ModalAnalysisSpecification(

*See sub-skills for full details.*
### Extract Dominant DOFs

```python
from digitalmodel.orcaflex.orcaflex_modal_analysis import OrcModalAnalysis
import pandas as pd

modal = OrcModalAnalysis()

# After running analysis, get summary
all_modes_summary_df = modal.all_file_summary["Case1"]

# Filter modes dominated by specific DOF

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [viv-analysis](../viv-analysis/SKILL.md) - VIV susceptibility assessment
- [orcaflex-static-debug](../orcaflex-static-debug/SKILL.md) - Static convergence troubleshooting

## References

- OrcFxAPI Modal Analysis: Orcina Documentation
- DNV-RP-C205: Environmental Conditions and Environmental Loads
- API RP 2RD: Design of Risers for Floating Production Systems
- Source: `src/digitalmodel/modules/orcaflex/orcaflex_modal_analysis.py`
- Config: `src/digitalmodel/base_configs/modules/orcaflex/orcaflex_modal_analysis.yml`

## Sub-Skills

- [Basic Modal Analysis (+1)](basic-modal-analysis/SKILL.md)
- [Model Preparation (+2)](model-preparation/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [1. Static Equilibrium → Modal Analysis](1-static-equilibrium-modal-analysis/SKILL.md)
- [Mode Shapes CSV (+2)](mode-shapes-csv/SKILL.md)
- [DOF Percentage Calculation (+2)](dof-percentage-calculation/SKILL.md)
- [Common Errors and Fixes (+1)](common-errors-and-fixes/SKILL.md)
- [Expected Frequency Ranges (+1)](expected-frequency-ranges/SKILL.md)
- [With VIV Analysis (+1)](with-viv-analysis/SKILL.md)
