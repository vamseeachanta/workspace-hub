---
name: mesh-utilities-1-quick-mesh-inspection
description: 'Sub-skill of mesh-utilities: 1. Quick Mesh Inspection (+5).'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# 1. Quick Mesh Inspection (+5)

## 1. Quick Mesh Inspection


```python
from digitalmodel.hydrodynamics.bemrosetta.mesh import GDFHandler
from pathlib import Path

def inspect_mesh(mesh_path: str) -> dict:
    """Quick inspection of panel mesh file."""
    path = Path(mesh_path)

    if path.suffix.lower() == '.gdf':
        handler = GDFHandler()

*See sub-skills for full details.*

## 2. Format Conversion


```python
from digitalmodel.hydrodynamics.diffraction.mesh_pipeline import MeshPipeline

def convert_mesh(
    input_path: str,
    output_format: str,
    output_dir: str = "."
) -> str:
    """Convert mesh between formats (GDF, DAT, STL)."""
    pipeline = MeshPipeline()

*See sub-skills for full details.*

## 3. Quality Validation


```python
from digitalmodel.hydrodynamics.diffraction.geometry_quality import (
    GeometryQualityChecker,
)

def validate_mesh_quality(mesh_path: str) -> dict:
    """Run full quality validation on mesh."""
    checker = GeometryQualityChecker()
    report = checker.generate_report(mesh_path)


*See sub-skills for full details.*

## 4. Prepare Mesh for Solver


```python
from digitalmodel.hydrodynamics.diffraction.mesh_pipeline import MeshPipeline

def prepare_for_solver(
    mesh_path: str,
    solver: str,
    output_dir: str = "solver_input"
) -> str:
    """Prepare mesh for specific solver with validation.


*See sub-skills for full details.*

## 5. Mesh Coarsening (Decimation)


```python
import numpy as np
from pathlib import Path

def coarsen_mesh_simple(
    mesh_path: str,
    target_panels: int,
    output_path: str = None
) -> str:
    """Simple mesh coarsening by vertex clustering.

*See sub-skills for full details.*

## 6. GMSH-Based Mesh Generation


```python
from digitalmodel.solvers.gmsh_meshing import GMSHMeshGenerator

def generate_simple_hull_mesh(
    length: float,
    beam: float,
    draft: float,
    panel_size: float = 2.0,
    output_path: str = "hull.gdf"
) -> str:

*See sub-skills for full details.*
