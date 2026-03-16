---
name: gmsh-meshing-quality-metrics
description: 'Sub-skill of gmsh-meshing: Quality Metrics (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Quality Metrics (+1)

## Quality Metrics


```python
def check_mesh_quality(msh_file: str):
    """Check mesh quality metrics."""
    gmsh.initialize()
    gmsh.open(msh_file)

    # Get quality statistics
    # Gamma: inscribed/circumscribed radius ratio (1.0 = perfect)
    # Eta: quality measure based on edge lengths
    # Rho: another quality measure

*See sub-skills for full details.*

## BEM-Specific Quality Checks


- **Adjacent panel ratio**: Ratio between neighboring panel areas should be < 2:1. Gradual variation is acceptable even with large global min/max ratio.
- **Normals consistency**: All panel normals must point outward (into the fluid domain).
- **Watertightness**: No gaps between panels (shared nodes on edges).
- **Panel planarity**: For quad panels, all 4 nodes should be nearly coplanar.

See `skills/engineering/marine-offshore/mesh-utilities/SKILL.md` for mesh inspection tools.
