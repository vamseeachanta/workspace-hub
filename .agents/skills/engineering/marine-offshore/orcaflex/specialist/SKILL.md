---
name: orcaflex-specialist
version: 1.0.0
category: engineering
description: Automate OrcaFlex marine simulations via Python API for mooring, riser,
  and installation analysis
type: reference
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Specialist

## When to Use This Skill

Use this skill when you need to:
- Automate OrcaFlex model creation and analysis
- Build parametric OrcaFlex models via Python API
- Perform batch simulations with varying parameters
- Extract and process time series results
- Validate OrcaFlex models against design criteria
- Integrate OrcaFlex with external tools and workflows
- Optimize mooring and riser configurations
- Conduct sensitivity studies and Monte Carlo simulations

## Core Knowledge Areas

### 1. OrcaFlex Python API Basics

Connecting to OrcaFlex and basic model operations:

```python
import OrcFxAPI
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

def create_new_model(
    general_data: dict,

*See sub-skills for full details.*
### 2. Building Models Programmatically

Create complex models via Python API:

```python
def create_vessel_model(
    vessel_params: dict,
    mooring_config: dict,
    environment: dict
) -> OrcFxAPI.Model:
    """
    Create complete vessel model with moorings and environment.

*See sub-skills for full details.*
### 3. Results Extraction and Post-Processing

Extract time series and perform analysis:

```python
def extract_time_series(
    model: OrcFxAPI.Model,
    object_name: str,
    variable_name: str,
    object_extra: OrcFxAPI.OrcaFlexObjectExtra = OrcFxAPI.oeEndA,
    period: OrcFxAPI.SpecifiedPeriod = OrcFxAPI.SpecifiedPeriod(OrcFxAPI.pnWholeSimulation)
) -> tuple:

*See sub-skills for full details.*
### 4. Batch Simulation and Parametric Studies

Automate multiple simulation runs:

```python
def batch_simulation(
    base_model_path: Path,
    parameter_sets: List[dict],
    output_dir: Path,
    parallel: bool = False
) -> List[dict]:
    """

*See sub-skills for full details.*
### 5. Model Validation and QA

Automated model checking:

```python
def validate_model(
    model: OrcFxAPI.Model,
    checks: List[str] = None
) -> dict:
    """
    Comprehensive model validation checks.


*See sub-skills for full details.*
### 6. Advanced Analysis Techniques

```python
def extreme_response_analysis(
    model_path: Path,
    sea_states: List[dict],
    response_variable: tuple,
    method: str = 'most_probable_maximum'
) -> dict:
    """
    Extreme response analysis using irregular wave simulations.


*See sub-skills for full details.*

## Complete Examples

### Example 1: Automated Mooring Analysis Workflow

```python
from pathlib import Path
import OrcFxAPI
import numpy as np
import pandas as pd

def complete_mooring_analysis_workflow(
    vessel_params: dict,
    mooring_config: dict,
    environment: dict,

*See sub-skills for full details.*

## Resources

### OrcaFlex Documentation

- **OrcaFlex Help**: Built-in help system (F1 in OrcaFlex)
- **Python API Reference**: OrcaFlex installation → Python folder → OrcFxAPIDocumentation.html
- **Example Scripts**: OrcaFlex → Examples → Python folder
- **Orcina Website**: https://www.orcina.com/resources/
### Training and Support

- **Orcina Training Courses**: Official OrcaFlex training
- **User Forum**: https://www.orcina.com/forums/
- **Technical Support**: support@orcina.com
### Related Standards

- **DNV-RP-C205**: Environmental Conditions and Environmental Loads
- **DNV-RP-F205**: Global Performance Analysis of Deepwater Floating Structures
- **API RP 2SM**: Recommended Practice for Design, Manufacture, Installation, and Maintenance of Synthetic Fiber Ropes
- **API RP 2SK**: Design and Analysis of Stationkeeping Systems for Floating Structures
### Additional Resources

- Noble Denton (2013). *OrcaFlex Training Manual*
- Orcina (2023). *OrcaFlex Manual Version 11.4*
- Various industry webinars and tutorials on YouTube

---

**Use this skill for:** Expert-level OrcaFlex modeling, automation, and analysis for offshore marine simulations with full Python API integration.

## Sub-Skills

- [1. Model Organization (+2)](1-model-organization/SKILL.md)
