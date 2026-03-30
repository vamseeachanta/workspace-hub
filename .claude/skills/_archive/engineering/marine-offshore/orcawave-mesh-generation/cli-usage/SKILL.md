---
name: orcawave-mesh-generation-cli-usage
description: 'Sub-skill of orcawave-mesh-generation: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Generate mesh from STL
python -m digitalmodel.orcawave.mesh generate \
    --input geometry/hull.stl \
    --output geometry/hull.gdf \
    --panels 3000 \
    --symmetry port-starboard

# Validate existing mesh
python -m digitalmodel.orcawave.mesh validate \
    --input geometry/hull.gdf \
    --report validation_report.html

# Run convergence study
python -m digitalmodel.orcawave.mesh convergence \
    --geometry geometry/hull.stl \
    --levels 500,1000,2000,4000 \
    --output results/convergence/

# Convert STL to GDF
python -m digitalmodel.orcawave.converters stl-to-gdf \
    --input geometry/hull.stl \
    --output geometry/hull.gdf \
    --scale 0.001  # mm to m
```
