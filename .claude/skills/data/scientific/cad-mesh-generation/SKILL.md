---
name: cad-mesh-generation
version: 1.0.0
category: data
description: Generate parametric CAD geometry and finite element meshes using FreeCAD
  and GMSH
capabilities: []
requires: []
see_also:
- cad-mesh-generation-1-parametric-design
tags: []
---

# Cad Mesh Generation

## When to Use This Skill

Use this skill when you need to:
- Create parametric CAD models of vessels, platforms, or structures
- Generate meshes for finite element analysis (FEA)
- Generate panel meshes for boundary element methods (BEM/hydrodynamics)
- Automate geometry creation for marine structures
- Export geometry to AQWA, WAMIT, ANSYS, or other analysis tools
- Create complex geometries programmatically with Python
- Perform mesh quality checks and refinement

## Core Knowledge Areas

### 1. FreeCAD Python Scripting Basics

Creating geometry with FreeCAD Python API:

```python
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

# Try to import FreeCAD, provide fallback for development
try:

*See sub-skills for full details.*
### 2. GMSH Mesh Generation

Creating meshes with GMSH Python API:

```python
# Try to import gmsh
try:
    import gmsh
    GMSH_AVAILABLE = True
except ImportError:
    GMSH_AVAILABLE = False
    print("Warning: GMSH not available, using mock")

*See sub-skills for full details.*
### 3. Mesh Quality Assessment

Check mesh quality metrics:

```python
def analyze_mesh_quality(
    mesh_file: Path,
    mesh_type: str = 'surface'
) -> dict:
    """
    Analyze mesh quality metrics.


*See sub-skills for full details.*
### 4. Mesh Conversion for Analysis Tools

Convert meshes to various formats:

```python
def convert_mesh_to_wamit_gdf(
    mesh_file: Path,
    output_file: Path,
    symmetry: str = 'none'
) -> None:
    """
    Convert GMSH mesh to WAMIT .gdf format.

*See sub-skills for full details.*

## Complete Examples

### Example 1: Complete Vessel Geometry and Mesh Workflow

```python
from pathlib import Path
import numpy as np

def complete_vessel_geometry_workflow(
    vessel_params: dict,
    mesh_params: dict,
    output_dir: Path
) -> dict:
    """

*See sub-skills for full details.*

## Resources

### FreeCAD

- **Documentation**: https://wiki.freecadweb.org/
- **Python API**: https://wiki.freecadweb.org/Python_scripting_tutorial
- **Examples**: https://github.com/FreeCAD/FreeCAD/tree/master/src/Mod/Part/TestPartApp
### GMSH

- **Documentation**: https://gmsh.info/doc/texinfo/gmsh.html
- **Python API**: http://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API
- **Tutorials**: https://gitlab.onelab.info/gmsh/gmsh/-/tree/master/tutorials
### Mesh Generation

- **Netgen**: https://ngsolve.org/
- **TetGen**: http://wias-berlin.de/software/tetgen/
- **Triangle**: https://www.cs.cmu.edu/~quake/triangle.html
### Marine Geometry

- **DelftShip**: Free ship hull design software
- **MAXSURF**: Professional naval architecture software
- **Rhinoceros**: Advanced 3D modeling (with Grasshopper for parametric)

---

**Use this skill for:** Expert CAD geometry creation and mesh generation for marine structures with full export capabilities to analysis software.

## Sub-Skills

- [1. Parametric Design (+2)](1-parametric-design/SKILL.md)
