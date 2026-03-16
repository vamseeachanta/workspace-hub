---
name: orcawave-mesh-generation
description: Panel mesh generation and optimization specialist for OrcaWave diffraction
  analysis. Handles CAD-to-panel mesh conversion, mesh quality validation, convergence
  studies, and GDF file generation for hydrodynamic computations.
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
see_also:
- orcawave-mesh-generation-version-metadata
- orcawave-mesh-generation-standard-mesh-generation
- orcawave-mesh-generation-panel-quality-thresholds
- orcawave-mesh-generation-cli-usage
- orcawave-mesh-generation-integration-with-gmsh-meshing-skill
tags: []
scripts_exempt: true
---

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

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - Main diffraction analysis
- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Advanced mesh generation
- [freecad-automation](../freecad-automation/SKILL.md) - CAD geometry preparation
- [cad-engineering](../cad-engineering/SKILL.md) - CAD file format handling

## References

- OrcaWave GDF File Format Specification
- Orcina Panel Method Documentation
- WAMIT Manual (GDF format compatibility)
- Lee, C.H.: WAMIT Theory Manual

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with mesh generation, validation, and convergence study capabilities

## Sub-Skills

- [Geometry Import (+2)](geometry-import/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Standard Mesh Generation (+1)](standard-mesh-generation/SKILL.md)
- [Panel Quality Thresholds (+1)](panel-quality-thresholds/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Integration with gmsh-meshing Skill](integration-with-gmsh-meshing-skill/SKILL.md)
