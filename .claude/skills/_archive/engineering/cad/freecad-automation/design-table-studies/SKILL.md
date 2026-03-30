---
name: freecad-automation-design-table-studies
description: 'Sub-skill of freecad-automation: Design table batch parametric studies — hull hydrostatics and FEM parameter sweeps with YAML export.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Design Table Studies

## Overview

Batch parametric studies for hull hydrostatics and FEM structural analysis. Enumerate parameter combinations, run analyses, and export comparison results.

## Hull Hydrostatics Mode

```python
from digitalmodel.visualization.design_tools.design_table import DesignTable
from digitalmodel.hydrodynamics.hull_library.profile_schema import HullProfile

profile = HullProfile.load_yaml("base_hull.yaml")
dt = DesignTable(profile)
dt.add_parameter("length_bp", [90.0, 100.0, 110.0])
dt.add_parameter("beam", [18.0, 20.0, 22.0])
dt.generate_variations()  # 9 combinations
results = dt.run_batch_hydrostatics(parallel=True)
dt.export_results_yaml(Path("hydro_comparison.yaml"))
```

### Scalable Parameters

`length_bp`, `beam`, `draft`, `depth`, `block_coefficient`

Stations are proportionally rescaled when dimensions change.

## FEM Batch Mode

```python
from digitalmodel.visualization.design_tools.design_table import DesignTable

dt = DesignTable.for_fem()
dt.add_fem_parameter("hole_radius", [8.0, 10.0, 12.0, 15.0])
results = dt.run_batch_fem(work_dir=Path("/tmp/fem_study"))
dt.export_fem_results_yaml(Path("fem_comparison.yaml"))

# Results include Kt for each variation
for r in results:
    print(f"r={r['parameters']['hole_radius']:.0f} → Kt={r['kt']:.3f}")
```

### FEM Parameters

`hole_radius`, `plate_width`, `plate_height`, `thickness`, `element_size`, `youngs_modulus`

Each combination runs a full FEMChain plate-with-hole analysis.

## YAML Output Format

### Hydrostatics

```yaml
base_profile: hull_name
n_variations: 9
variations:
  - index: 0
    parameters: {length_bp: 90.0, beam: 18.0, draft: 8.0, depth: 10.0}
    hydrostatics: {displaced_volume: 12960.0, waterplane_area: 1620.0, ...}
```

### FEM

```yaml
mode: fem_batch
n_variations: 4
variations:
  - index: 0
    parameters: {hole_radius: 8.0, plate_width: 200.0, ...}
    kt: 2.85
    max_von_mises: 285.0
```

## Validated Behaviour

- Kt increases monotonically with hole_radius / plate_width ratio
- Box barge hydrostatics match analytical (V, Awp, KB, BM) within 2%
