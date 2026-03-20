---
name: workstations-routing-rules
description: 'Sub-skill of workstations: Routing Rules.'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Routing Rules

## Routing Rules


Use when setting `computer:` on a new WRK item:

| Keyword in WRK title / tags | Recommended machine |
|-----------------------------|---------------------|
| orcaflex, ansys, aqwa | licensed-win-1 |
| office, windows, excel | licensed-win-2 or licensed-win-1 |
| heavy-compute, large-sim, cfd-hpc, fea-hpc | gali-linux-compute-1 |
| blender, animation, openfoam, gmsh, calculix, fenics, freecad, elmer | dev-secondary |
| worldenergydata, hub, claude, orchestration | dev-primary |
| open-source-dev, digitalmodel, assetutilities | dev-primary or dev-secondary |
| everything else | dev-primary |
