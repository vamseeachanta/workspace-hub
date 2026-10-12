---
name: orcaflex-installation-analysis
description: Create and analyze OrcaFlex models for offshore installation sequences
  including subsea structure lowering, pipeline installation, and crane operations.
  Generate models at multiple water depths and orientations for installation feasibility
  studies.
type: reference
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
from digitalmodel.solvers.orcaflex.orcaflex_installation import OrcInstallation

# Initialize
installer = OrcInstallation()

# Configuration for depth variation
cfg = {
    "structure": {
        "BaseFile": "reference.yml",

*See sub-skills for full details.*
### Simple Depth Model Generation

```python
from digitalmodel.solvers.orcaflex.orcaflex_installation import OrcInstallation

installer = OrcInstallation()

# Simpler configuration
cfg = {
    "reference_elevation_file": "models/reference.yml",
    "structure": "Subsea_Template",
    "masterlink": "Lifting_Point",

*See sub-skills for full details.*
### With Structure Orientation

```python
from digitalmodel.solvers.orcaflex.orcaflex_installation import OrcInstallation

installer = OrcInstallation()

# This generates:
# 1. Base model at each depth
# 2. Orientation variant (rotation about Z)
cfg = {
    "structure": {

*See sub-skills for full details.*

## Related Skills

- orcaflex-modeling - Run OrcaFlex simulations
- orcaflex-post-processing - Extract results
- orcaflex-static-debug - Debug convergence issues
- orcaflex-line-wizard - Configure line properties

## References

- OrcaFlex Installation Analysis: Orcina Documentation
- DNV-RP-H103: Modelling and Analysis of Marine Operations
- API RP 2A: Planning, Designing and Constructing Fixed Offshore Platforms
- Source: `src/digitalmodel/solvers/orcaflex/orcaflex_installation.py`

## Sub-Skills

- Basic Installation Depth Study (+1)
- Model Preparation (+2)

## Sub-Skills

- Version Metadata
- [1.0.0] - 2026-01-17
- Installation Sequence Workflow
- Output File Structure
- Reference Elevation File (+2)
- Integration with Universal Runner
- 1. Splash Zone Analysis (+2)
- Post-Processing Installation Results
- Common Errors and Fixes (+3)
