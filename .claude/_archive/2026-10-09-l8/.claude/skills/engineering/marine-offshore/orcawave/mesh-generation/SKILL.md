---
name: orcawave-mesh-generation
description: Panel mesh generation for OrcaWave diffraction analysis. Use when converting
  CAD/STL to panel mesh, validating mesh quality, running convergence studies, or
  generating GDF files for hydrodynamic computations.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- panel mesh generation
- OrcaWave mesh
- GDF file creation
- mesh convergence study
- waterline refinement
- mesh quality validation
- CAD to panel mesh
- STL to GDF conversion
- mesh aspect ratio
- watertight mesh
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

<!-- ace:api-missing-warning -->
> [!WARNING]
> **Part of the Python API documented below does not exist in
> `digitalmodel`.** These snippets are a *specification* of intended
> capability, not runnable code. Do not import them, and do not report
> a result obtained by pretending they ran.
>
> Absent as of this revision:
>   - `digitalmodel.orcawave.converters`
>   - `digitalmodel.orcawave.converters.STLtoGDFConverter`
>   - `digitalmodel.orcawave.mesh`
>   - `digitalmodel.orcawave.mesh.OrcaWaveMeshGenerator`
>   - `digitalmodel.orcawave.mesh.WaterlineRefiner`
>   - `digitalmodel.orcawave.mesh_study`
>   - `digitalmodel.orcawave.mesh_study.MeshConvergenceStudy`
>
> The surrounding engineering content — method, conventions, what to
> watch for — is unaffected and remains usable.
>
> **The intended API is now specified in `digitalmodel`**, at
> `docs/domains/orcawave/intended-api/mesh-generation.md`, where it is a build
> target rather than something an agent may mistake for working code.
> Tracked in aceengineer-strategy#267, digitalmodel#2045.

<!-- ace:known-missing: digitalmodel.orcawave.converters, digitalmodel.orcawave.converters.STLtoGDFConverter, digitalmodel.orcawave.mesh, digitalmodel.orcawave.mesh.OrcaWaveMeshGenerator, digitalmodel.orcawave.mesh.WaterlineRefiner, digitalmodel.orcawave.mesh_study, digitalmodel.orcawave.mesh_study.MeshConvergenceStudy -->

# Orcawave Mesh Generation

## When to Use

- Converting CAD geometry (STL, OBJ, STEP) to OrcaWave panel mesh
- Generating GDF (Geometry Definition File) for OrcaWave
- Running mesh convergence studies
- Validating mesh quality (watertight, normals, aspect ratio)
- Optimizing waterline panel refinement
- Checking symmetry and enforcing port/starboard symmetry
- Preparing multi-body meshes with proper separation

## Python API

### Basic Mesh Generation

```python
from digitalmodel.orcawave.mesh import OrcaWaveMeshGenerator

# Initialize generator
generator = OrcaWaveMeshGenerator()

# Load CAD geometry
generator.load_geometry("geometry/hull.stl")

# Generate panel mesh

*See sub-skills for full details.*
### Mesh Convergence Study

```python
from digitalmodel.orcawave.mesh_study import MeshConvergenceStudy

# Initialize study
study = MeshConvergenceStudy()

# Define mesh sizes to test
mesh_configs = [
    {"target_panels": 500, "label": "coarse"},
    {"target_panels": 1000, "label": "medium"},
]

*See sub-skills for full details.*
### STL to GDF Conversion

```python
from digitalmodel.orcawave.converters import STLtoGDFConverter

# Initialize converter
converter = STLtoGDFConverter()

# Convert with options
converter.convert(
    input_file="geometry/hull.stl",
    output_file="geometry/hull.gdf",

*See sub-skills for full details.*
### Waterline Refinement

```python
from digitalmodel.orcawave.mesh import WaterlineRefiner

# Initialize refiner
refiner = WaterlineRefiner()

# Load existing mesh
refiner.load_mesh("geometry/hull_coarse.gdf")

# Apply waterline refinement

*See sub-skills for full details.*

## Related Skills

- orcawave-analysis - Main diffraction analysis
- gmsh-meshing - Advanced mesh generation
- freecad-automation - CAD geometry preparation
- cad-engineering - CAD file format handling

## References

- OrcaWave GDF File Format Specification
- Orcina Panel Method Documentation
- WAMIT Manual (GDF format compatibility)
- Lee, C.H.: WAMIT Theory Manual

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with mesh generation, validation, and convergence study capabilities

## Sub-Skills

- Geometry Import (+2)
- Best Practices

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- Standard Mesh Generation (+1)
- Panel Quality Thresholds (+1)
- CLI Usage
- Integration with gmsh-meshing Skill


## Documentation Reference

OrcaWave topics (`data/llm-wiki/orcawave/`):
- `Data,Meshfileformats.md` -- supported mesh file formats (GDF, etc.)
- `Data,Meshdetails.md` -- panel mesh detail parameters
- `Data,Bodies.md` -- body-to-mesh assignment
- `Meshview.md` -- mesh visualization and inspection
- `Meshview,Viewcontrol.md` -- mesh view navigation
- `Data,Validation.md` -- mesh validation checks

Papers (`data/llm-wiki/papers/`):
- `OrcaWave-working-with-meshes.md` -- comprehensive mesh guidance (panel sizing, waterline, symmetry)
- `Buoy-Discretisation.md` -- panel discretization for buoy geometries
