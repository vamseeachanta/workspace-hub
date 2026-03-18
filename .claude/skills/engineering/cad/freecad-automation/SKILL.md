---
name: freecad-automation
description: AI-powered automation agent for FreeCAD CAD operations including natural
  language processing, batch processing, parametric design, and marine engineering
  applications. Use for CAD automation, drawing generation, FEM preprocessing, and
  integration with offshore analysis tools.
version: 2.0.0
updated: 2026-03-16
category: engineering
triggers:
- FreeCAD automation
- parametric modeling
- CAD batch processing
- technical drawings
- assembly management
- FEM preprocessing
- hull design
- marine CAD
- .FCStd files
- Python scripting CAD
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- freecad-automation-version-metadata
- freecad-automation-200-2026-03-16
- freecad-automation-core-capabilities
- freecad-automation-command-line-interface
- freecad-automation-batch-processing-patterns
- freecad-automation-output-formats
- freecad-automation-swarm-coordination
- freecad-automation-performance-metrics
- freecad-automation-freecad-import-error
- freecad-automation-extract-geometry-properties
- freecad-automation-common-failures
- freecad-automation-geometry-validation-checks
- freecad-automation-parametric-hull-workflow
- freecad-automation-fem-chain-workflow
- freecad-automation-design-table-studies
tags: []
scripts_exempt: true
---

# FreeCAD Automation

## When to Use

- CAD automation and scripting
- Batch processing of FreeCAD files
- Parametric design and design tables
- Assembly management and constraint solving
- FEM preprocessing and mesh generation (CalculiX / gmsh)
- Drawing generation with automatic dimensioning
- Marine engineering hull design and hydrostatics
- NURBS hull generation from HullProfile stations
- CalculiX FEM structural analysis
- STEP import / volume mesh / INP export pipeline
- Design table batch parametric studies
- Natural language CAD commands
- Integration with OrcaFlex/AQWA workflows

## Prerequisites

- Python 3.8+
- FreeCAD 1.0+ (November 2024 release)
- `digitalmodel` package installed

## Python API

### Basic Operations

```python
from digitalmodel.agents.freecad import FreeCADAgent

agent = FreeCADAgent()
result = agent.execute_prompt("Create a box 100x50x25mm with chamfered edges")
print(f"Created: {result['object_name']}")
print(f"Volume: {result['properties']['volume']} mm3")
```

### Batch Processing

```python
results = agent.batch_process(
    pattern="*.FCStd",
    input_directory="./models",
    operation="export_step",
    parallel_workers=4
)
```

*See sub-skills for full details.*

### Parametric Design

```python
agent.parametric_study(
    base_model="hull_template.FCStd",
    parameters={
        "length": [150, 175, 200, 225],
        "beam": [25, 30, 35],
        "draft": [10, 12, 15]
    },
    output_directory="hull_variations/",
    export_formats=["STEP", "STL"]
)
```

### Hull Generation + Hydrostatics

```python
from digitalmodel.hydrodynamics.hull_library.profile_schema import (
    HullProfile, HullStation, HullType
)
from digitalmodel.visualization.design_tools.freecad_hull import FreeCADHullGenerator
from digitalmodel.visualization.design_tools.hull_hydrostatics import HullHydrostatics
```

*See sub-skills for full details.*

### FEM Analysis Chain (CalculiX)

```python
from digitalmodel.solvers.calculix import FEMChain, INPWriter

chain = FEMChain(work_dir=Path("/tmp/fem"))
result = chain.run_plate_validation(sigma_applied=100.0)
# result['kt'] ~ 3.0 within 5%
```

*See sub-skills for full details.*

### STEP Import / Mesh / INP Export

```python
from digitalmodel.solvers.gmsh_meshing import GMSHMeshGenerator

with GMSHMeshGenerator() as gen:
    mesh = gen.generate_mesh_from_step("hull.step", element_size=0.5)
    gen.export_mesh_inp("hull.inp", title="Hull FEM model")
```

## Related Skills

- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Advanced mesh generation
- [cad-engineering](../cad-engineering/SKILL.md) - General CAD expertise
- [blender-interface](../blender/SKILL.md) - 3D visualization
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) - Hydrodynamic analysis

## References

- FreeCAD Documentation: https://wiki.freecad.org/
- FreeCAD Python API: https://wiki.freecad.org/Python_scripting_tutorial

## Version History

- **2.0.0** (2026-03-16): Hull NURBS generation, hydrostatics, CalculiX FEM, STEP/INP pipeline, design tables (WRK-1251)
- **1.1.0** (2026-02-24): Output parsing, failure diagnosis, validation (WRK-372)
- **1.0.0** (2025-01-02): Initial release

## Sub-Skills

- [Agent Settings (+1)](agent-settings/SKILL.md)
- [Version Metadata](version-metadata/SKILL.md)
- [[2.0.0] - 2026-03-16 (+1)](200-2026-03-16/SKILL.md)
- [Core Capabilities (+4)](core-capabilities/SKILL.md)
- [Command Line Interface](command-line-interface/SKILL.md)
- [Batch Processing Patterns](batch-processing-patterns/SKILL.md)
- [Output Formats](output-formats/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [Performance Metrics](performance-metrics/SKILL.md)
- [FreeCAD Import Error (+1)](freecad-import-error/SKILL.md)
- [Extract Geometry Properties (+2)](extract-geometry-properties/SKILL.md)
- [Common Failures (+2)](common-failures/SKILL.md)
- [Geometry Validation Checks (+1)](geometry-validation-checks/SKILL.md)
- [Parametric Hull Workflow](parametric-hull-workflow/SKILL.md)
- [FEM Chain Workflow](fem-chain-workflow/SKILL.md)
- [Design Table Studies](design-table-studies/SKILL.md)
