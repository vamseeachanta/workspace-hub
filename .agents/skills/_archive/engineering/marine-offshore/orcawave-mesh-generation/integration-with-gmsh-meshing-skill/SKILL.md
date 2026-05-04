---
name: orcawave-mesh-generation-integration-with-gmsh-meshing-skill
description: 'Sub-skill of orcawave-mesh-generation: Integration with gmsh-meshing
  Skill.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Integration with gmsh-meshing Skill

## Integration with gmsh-meshing Skill


For advanced meshing requirements, combine with the gmsh-meshing skill:

```python
from digitalmodel.solvers.gmsh_meshing.mesh_generator import GmshMeshGenerator
from digitalmodel.orcawave.converters import GmshToGDFConverter

# Generate high-quality mesh with gmsh
gmsh_gen = GmshMeshGenerator()
gmsh_mesh = gmsh_gen.generate(
    geometry="geometry/hull.step",
    element_size=0.5,
    refinement_fields=["waterline", "bilge_keel"]
)

# Convert to OrcaWave GDF format
converter = GmshToGDFConverter()
converter.convert(gmsh_mesh, "geometry/hull.gdf")
```
