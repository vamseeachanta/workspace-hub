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
| orcaflex, ansys, aqwa | acma-ansys05 |
| office, windows, excel | acma-ws014 or acma-ansys05 |
| heavy-compute, large-sim, cfd-hpc, fea-hpc | gali-linux-compute-1 |
| blender, animation, openfoam, gmsh, calculix, fenics, freecad, elmer | ace-linux-2 |
| worldenergydata, hub, claude, orchestration | ace-linux-1 |
| open-source-dev, digitalmodel, assetutilities | ace-linux-1 or ace-linux-2 |
| everything else | ace-linux-1 |
