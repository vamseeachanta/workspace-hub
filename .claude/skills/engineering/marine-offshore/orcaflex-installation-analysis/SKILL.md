---
name: orcaflex-installation-analysis
description: Create and analyze OrcaFlex models for offshore installation sequences
  including subsea structure lowering, pipeline installation, and crane operations.
  Generate models at multiple water depths and orientations for installation feasibility
  studies.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- installation analysis
- subsea installation
- structure lowering
- crane operation
- installation sequence
- depth variation
- installation feasibility
- heavy lift
- payload handling
capabilities: []
requires: []
see_also:
- orcaflex-installation-analysis-version-metadata
- orcaflex-installation-analysis-100-2026-01-17
- orcaflex-installation-analysis-installation-sequence-workflow
- orcaflex-installation-analysis-output-file-structure
- orcaflex-installation-analysis-reference-elevation-file
- orcaflex-installation-analysis-integration-with-universal-runner
- orcaflex-installation-analysis-1-splash-zone-analysis
- orcaflex-installation-analysis-post-processing-installation-results
- orcaflex-installation-analysis-common-errors-and-fixes
tags: []
scripts_exempt: true
---

# Orcaflex Installation Analysis

## When to Use

- Subsea structure installation analysis
- Pipeline/umbilical installation sequences
- Heavy lift crane operations
- Installation depth variation studies
- Lowering phase analysis
- Splash zone analysis
- Installation feasibility assessment
- Crane wire and sling configuration

## Prerequisites

- OrcaFlex license (for simulation)
- Python environment with `digitalmodel` package installed
- Reference model files (.yml format recommended)
- Reference elevation configuration

## Python API

### Generate Installation Depth Models

```python
from digitalmodel.orcaflex.orcaflex_installation import OrcInstallation

# Initialize
installer = OrcInstallation()

# Configuration for depth variation
cfg = {
    "structure": {
        "BaseFile": "reference.yml",

*See sub-skills for full details.*
### Simple Depth Model Generation

```python
from digitalmodel.orcaflex.orcaflex_installation import OrcInstallation

installer = OrcInstallation()

# Simpler configuration
cfg = {
    "reference_elevation_file": "models/reference.yml",
    "structure": "Subsea_Template",
    "masterlink": "Lifting_Point",

*See sub-skills for full details.*
### With Structure Orientation

```python
from digitalmodel.orcaflex.orcaflex_installation import OrcInstallation

installer = OrcInstallation()

# This generates:
# 1. Base model at each depth
# 2. Orientation variant (rotation about Z)
cfg = {
    "structure": {

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract results
- [orcaflex-static-debug](../orcaflex-static-debug/SKILL.md) - Debug convergence issues
- [orcaflex-line-wizard](../orcaflex-line-wizard/SKILL.md) - Configure line properties

## References

- OrcaFlex Installation Analysis: Orcina Documentation
- DNV-RP-H103: Modelling and Analysis of Marine Operations
- API RP 2A: Planning, Designing and Constructing Fixed Offshore Platforms
- Source: `src/digitalmodel/modules/orcaflex/orcaflex_installation.py`

## Sub-Skills

- [Basic Installation Depth Study (+1)](basic-installation-depth-study/SKILL.md)
- [Model Preparation (+2)](model-preparation/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Installation Sequence Workflow](installation-sequence-workflow/SKILL.md)
- [Output File Structure](output-file-structure/SKILL.md)
- [Reference Elevation File (+2)](reference-elevation-file/SKILL.md)
- [Integration with Universal Runner](integration-with-universal-runner/SKILL.md)
- [1. Splash Zone Analysis (+2)](1-splash-zone-analysis/SKILL.md)
- [Post-Processing Installation Results](post-processing-installation-results/SKILL.md)
- [Common Errors and Fixes (+3)](common-errors-and-fixes/SKILL.md)
