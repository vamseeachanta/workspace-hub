---
name: freecad-automation-parametric-hull-workflow
description: 'Sub-skill of freecad-automation: Parametric hull generation workflow — HullProfile definition, NURBS surface creation, STEP export, and manifold validation.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Parametric Hull Workflow

## Overview

Generate hull geometry from naval architecture parameters using the HullProfile → FreeCADHullGenerator → ManifoldChecker pipeline.

## Pipeline Steps

1. **Define HullProfile** — stations with (z, y) waterline offsets
2. **Generate NURBS surface** — FreeCADHullGenerator interpolates stations
3. **Validate geometry** — ManifoldChecker verifies watertight + no self-intersection
4. **Export STEP** — solid body for downstream FEM or CAD use (requires FreeCAD)

## Code Example

```python
from digitalmodel.hydrodynamics.hull_library.profile_schema import (
    HullProfile, HullStation, HullType,
)
from digitalmodel.visualization.design_tools.freecad_hull import FreeCADHullGenerator
from digitalmodel.visualization.design_tools.manifold_check import ManifoldChecker

# 1. Define hull
stations = [
    HullStation(x_position=x, waterline_offsets=[(0, y), (10, y)])
    for x, y in [(0, 0), (25, 8), (50, 10), (75, 8), (100, 0)]
]
profile = HullProfile(
    name="example", hull_type=HullType.SHIP,
    stations=stations, length_bp=100, beam=20, draft=8, depth=10,
    source="example",
)

# 2. Generate surface
gen = FreeCADHullGenerator(profile)
surface = gen.generate_nurbs_surface()
# surface["surface_type"] = "freecad" or "scipy"

# 3. Validate
checker = ManifoldChecker(surface["surface_points"])
result = checker.run_all_checks()
assert result["pass"]  # watertight + no self-intersection + consistent normals

# 4. Export (FreeCAD only)
gen.export_step(Path("hull.step"))
```

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `HullProfile` | `hydrodynamics.hull_library.profile_schema` | Hull definition with stations |
| `HullStation` | same | Single cross-section (z, y) offsets |
| `FreeCADHullGenerator` | `visualization.design_tools.freecad_hull` | NURBS surface + STEP export |
| `ManifoldChecker` | `visualization.design_tools.manifold_check` | Geometry validation |

## Conventions

- **Keel-up**: z=0 at keel, z=draft at waterline, z=depth at deck
- **Half-breadth**: y is distance from centreline (starboard side)
- **Stations sorted by x_position** (aft perpendicular = 0)
- Without FreeCAD: scipy-mode NURBS grid (numpy array) — no STEP export
