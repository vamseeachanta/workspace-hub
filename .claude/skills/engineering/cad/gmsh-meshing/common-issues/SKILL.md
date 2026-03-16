---
name: gmsh-meshing-common-issues
description: 'Sub-skill of gmsh-meshing: Common Issues (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


| Problem | Cause | Solution |
|---------|-------|----------|
| Empty mesh output | Missing `synchronize()` | Call `gmsh.model.geo.synchronize()` or `gmsh.model.occ.synchronize()` before meshing |
| Wrong element types | Default is triangles | Use `setRecombine()` for quads, or `RecombineAll` option |
| Poor quality at corners | Sharp angles | Add local refinement or increase `Mesh.Smoothing` |
| STEP import fails | Topology issues | Enable `Geometry.OCCFixDegenerated`, `OCCFixSmallEdges`, `OCCSewFaces` |
| MSH format not recognized | Wrong version | Set `Mesh.MshFileVersion` to 2.2 for BEM tools |
| Physical groups empty | Not assigned | Must define physical groups before `write()` |
| Transfinite fails | Incompatible topology | Surface must be 3 or 4-sided, curves must have matching node counts |
| Size fields ignored | Other size sources active | Disable `MeshSizeExtendFromBoundary`, `MeshSizeFromPoints`, `MeshSizeFromCurvature` |
| Crash on large models | Memory | Use `-nt` for parallel meshing, increase verbosity to find bottleneck |
| `gmsh` CLI: `/usr/bin/env: 'python': No such file or directory` | pip-installed gmsh wrapper uses `#!/usr/bin/env python` shebang | Fix shebang: `sed -i 's\|python$\|python3\|' ~/.local/bin/gmsh`; or use `/usr/bin/gmsh` (system binary) |
| pip gmsh shadows system gmsh | `~/.local/bin/gmsh` (pip wrapper) takes precedence over `/usr/bin/gmsh` (native) | Check `type -a gmsh`; pip version is Python-only (no GUI), system version has FLTK GUI |


## Debugging Tips


```python
# Enable verbose output
gmsh.option.setNumber("General.Verbosity", 99)

# Check model entities
print(gmsh.model.getEntities())  # All entities
print(gmsh.model.getEntities(dim=2))  # Surfaces only

# Check bounding box
xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)

# Visualize interactively
gmsh.fltk.run()  # Opens GUI

# Check mesh statistics
gmsh.model.mesh.generate(2)
node_tags, _, _ = gmsh.model.mesh.getNodes()
print(f"Number of nodes: {len(node_tags)}")
elem_types, elem_tags, _ = gmsh.model.mesh.getElements(dim=2)
total_elems = sum(len(t) for t in elem_tags)
print(f"Number of elements: {total_elems}")
```
