---
name: solver-benchmark-creating-benchmark-specs
description: 'Sub-skill of solver-benchmark: Creating Benchmark Specs.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Creating Benchmark Specs

## Creating Benchmark Specs


Use the standard DiffractionSpec YAML format:

```yaml
version: "1.0"
analysis_type: diffraction

vessel:
  name: "MyHull_Benchmark"
  type: "barge"
  geometry:
    mesh_file: "path/to/mesh.gdf"
    mesh_format: gdf
    symmetry: none
    reference_point: [0.0, 0.0, 0.0]
    waterline_z: 0.0
  inertia:
    mass: 1000.0  # kg
    centre_of_gravity: [0.0, 0.0, -0.5]
    radii_of_gyration: [1.0, 1.0, 1.0]

environment:
  water_depth: 100.0
  water_density: 1025.0
  gravity: 9.80665


*See sub-skills for full details.*
