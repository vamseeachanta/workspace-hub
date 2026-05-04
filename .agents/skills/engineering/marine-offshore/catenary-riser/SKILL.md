---
name: catenary-riser
description: Analyze catenary and lazy wave riser configurations for static shape,
  forces, and OrcaFlex model generation. Use for riser static configuration analysis,
  catenary force calculations, lazy wave design, and generating OrcaFlex models from
  catenary parameters.
type: reference
updated: '2026-01-07'
capabilities: []
requires: []
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

# Catenary Riser

## When to Use

- Catenary riser static analysis
- Lazy wave catenary design and optimization
- Riser static configuration calculation
- Catenary force and tension analysis
- Generating OrcaFlex models from catenary geometry
- Fatigue loading extraction from riser configurations
- Pipe property calculations (buoyancy, effective weight)

## Prerequisites

- Python environment with `digitalmodel` package installed
- Riser geometry and material properties
- Environmental data (water depth, current if applicable)

## Python API

### Simple Catenary Equation

```python
from digitalmodel.subsea.catenary.catenary_equation import CatenaryEquation
import numpy as np

catenary = CatenaryEquation()
top_end = (0.0, 100.0)
touchdown = (500.0, 0.0)

horizontal_tension = catenary.solve(
    top_end=top_end,

*See sub-skills for full details.*
### Catenary Riser Analysis

```python
from digitalmodel.subsea.catenary.catenary_riser import CatenaryRiser
from digitalmodel.subsea.catenary.pipe_properties import PipeProperties

pipe = PipeProperties(
    outer_diameter=0.2032,
    wall_thickness=0.0127,
    steel_density=7850,
    internal_fluid_density=800
)

*See sub-skills for full details.*
### Lazy Wave Catenary

```python
from digitalmodel.subsea.catenary.lazy_wave_catenary import LazyWaveCatenary

lazy_wave = LazyWaveCatenary()
config = {
    "water_depth": 1500.0,
    "hang_off_angle": 8.0,
    "buoyancy_section": {
        "start_length": 800.0,
        "end_length": 1200.0,

*See sub-skills for full details.*
### OrcaFlex Model Building

```python
from digitalmodel.subsea.catenary.orcaflex_model import OrcaFlexModelBuilder

builder = OrcaFlexModelBuilder()
builder.set_line_from_catenary(
    catenary_results=results,
    line_name="Riser1",
    segment_length=5.0
)
builder.add_buoyancy_section(

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `CatenaryEquation` | Mathematical catenary solver |
| `CatenaryRiser` | Main analysis orchestrator |
| `LazyWaveCatenary` | Dynamic catenary with buoyancy |
| `PipeProperties` | Material and geometric properties |
| `OrcaFlexModelBuilder` | Model export to OrcaFlex |

## Related Skills

- [orcaflex/modeling](../orcaflex/modeling/SKILL.md) - Run OrcaFlex simulations
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Fatigue at critical locations
- [structural-analysis](../structural-analysis/SKILL.md) - Stress verification

## References

- API RP 2RD: Design of Risers for Floating Production Systems
- DNV-OS-F201: Dynamic Risers

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [1. Simple Catenary Analysis (+2)](1-simple-catenary-analysis/SKILL.md)
- [Catenary Shape CSV](catenary-shape-csv/SKILL.md)
