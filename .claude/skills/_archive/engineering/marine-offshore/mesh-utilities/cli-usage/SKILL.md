---
name: mesh-utilities-cli-usage
description: 'Sub-skill of mesh-utilities: CLI Usage.'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Quick inspection
uv run python -c "from mesh_utilities import inspect_mesh; inspect_mesh('vessel.gdf')"

# Quality check
uv run python -c "from mesh_utilities import validate_mesh_quality; validate_mesh_quality('hull.gdf')"

# Conversion
uv run python -c "from mesh_utilities import convert_mesh; convert_mesh('hull.stl', 'gdf', 'output/')"

# Pre-solver check
uv run python -c "from mesh_utilities import pre_solver_checklist; pre_solver_checklist('model.gdf', 'orcawave')"
```
