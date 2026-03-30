---
name: orcawave-mesh-generation-standard-mesh-generation
description: 'Sub-skill of orcawave-mesh-generation: Standard Mesh Generation (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Standard Mesh Generation (+1)

## Standard Mesh Generation


```yaml
# configs/mesh_generation.yml

mesh_generation:
  input:
    file: "geometry/fpso_hull.stl"
    format: "stl"
    units: "meters"

  parameters:

*See sub-skills for full details.*

## Convergence Study Configuration


```yaml
# configs/convergence_study.yml

convergence_study:
  geometry: "geometry/vessel.stl"

  mesh_levels:
    - panels: 500
      label: "Level 1 (Coarse)"
    - panels: 1000

*See sub-skills for full details.*
