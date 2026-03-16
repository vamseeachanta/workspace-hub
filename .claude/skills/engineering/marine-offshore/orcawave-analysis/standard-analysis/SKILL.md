---
name: orcawave-analysis-standard-analysis
description: 'Sub-skill of orcawave-analysis: Standard Analysis (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Standard Analysis (+1)

## Standard Analysis


```yaml
# configs/orcawave_analysis.yml

orcawave:
  vessel:
    name: "FPSO"
    mesh_file: "geometry/hull_panels.dat"
    mass: 250000.0  # tonnes
    cog: [150.0, 0.0, 15.0]  # m
    radii_of_gyration: [25.0, 80.0, 82.0]  # m

*See sub-skills for full details.*

## Multi-Body Analysis


```yaml
orcawave:
  multi_body:
    enabled: true
    bodies:
      - name: "FPSO"
        mesh_file: "geometry/fpso_panels.dat"
        position: [0, 0, 0]
      - name: "Offloading_Tanker"
        mesh_file: "geometry/tanker_panels.dat"

*See sub-skills for full details.*
