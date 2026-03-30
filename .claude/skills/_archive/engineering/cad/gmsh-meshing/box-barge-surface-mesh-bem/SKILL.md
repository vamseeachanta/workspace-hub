---
name: gmsh-meshing-box-barge-surface-mesh-bem
description: 'Sub-skill of gmsh-meshing: Box Barge Surface Mesh (BEM) (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Box Barge Surface Mesh (BEM) (+4)

## Box Barge Surface Mesh (BEM)


Typical marine box barge for hydrodynamic BEM analysis. Only the wetted surface is meshed (no deck).

```python
import gmsh
import numpy as np

def create_box_barge_mesh(
    length: float,
    beam: float,
    draft: float,

*See sub-skills for full details.*

## Cylinder Panel Mesh


```python
def create_cylinder_mesh(
    radius: float,
    draft: float,
    mesh_size: float = 1.0,
    output_file: str = "cylinder.msh"
):
    """Create cylinder wetted surface mesh for BEM analysis."""
    gmsh.initialize()
    gmsh.model.add("cylinder")

*See sub-skills for full details.*

## STEP/STL Import and Remesh


```python
def remesh_step_file(
    step_file: str,
    mesh_size: float = 1.0,
    output_file: str = "remeshed.msh"
):
    """Import STEP geometry and generate new mesh."""
    gmsh.initialize()
    gmsh.model.add("imported")


*See sub-skills for full details.*

## Transfinite Structured Mesh


```python
def create_structured_plate(
    lx: float, ly: float,
    nx: int, ny: int,
    output_file: str = "plate.msh"
):
    """Create a structured quad mesh on a rectangular plate."""
    gmsh.initialize()
    gmsh.model.add("plate")


*See sub-skills for full details.*

## Field-Based Refinement


```python
def create_refined_mesh(output_file: str = "refined.msh"):
    """Mesh with distance-based refinement near a feature."""
    gmsh.initialize()
    gmsh.model.add("refined")

    # Create geometry (example: plate with hole)
    gmsh.model.occ.addRectangle(0, 0, 0, 20, 10)
    gmsh.model.occ.addDisk(10, 5, 0, 2, 2)
    gmsh.model.occ.cut([(2, 1)], [(2, 2)])

*See sub-skills for full details.*
