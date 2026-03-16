---
name: orcawave-mesh-generation-geometry-import
description: 'Sub-skill of orcawave-mesh-generation: Geometry Import (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Geometry Import (+2)

## Geometry Import

- **STL Import**: Triangulated surface meshes
- **OBJ Import**: Wavefront object files
- **STEP/IGES Import**: CAD solid models (via FreeCAD/gmsh)
- **GDF Import/Export**: OrcaWave native format


## Mesh Generation

- **Panel Discretization**: Quadrilateral and triangular panels
- **Waterline Refinement**: Finer mesh near free surface
- **Symmetry Handling**: Port/starboard symmetry detection and enforcement
- **Multi-body Meshing**: Separate meshes for coupled analysis


## Quality Validation

- **Watertight Check**: Closed surface validation
- **Normal Orientation**: Outward-pointing normals
- **Aspect Ratio**: Panel shape quality (target < 3:1)
- **Skewness**: Panel distortion metrics
- **Panel Count**: Optimal range 1000-5000 panels
