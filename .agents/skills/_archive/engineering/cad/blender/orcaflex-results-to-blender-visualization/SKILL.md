---
name: blender-interface-orcaflex-results-to-blender-visualization
description: 'Sub-skill of blender-interface: OrcaFlex Results to Blender Visualization
  (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex Results to Blender Visualization (+2)

## OrcaFlex Results to Blender Visualization


```python
"""Convert OrcaFlex line coordinates to Blender mesh for visualization."""
import bpy
import bmesh

def orcaflex_line_to_blender(positions, name="Riser", radius=0.1):
    """Create a Blender mesh from OrcaFlex line node positions.

    Args:
        positions: list of (x, y, z) tuples from OrcaFlex
        name: object name
        radius: tube radius for bevel
    """
    # Create curve from points
    curve_data = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius

    spline = curve_data.splines.new('POLY')
    spline.points.add(len(positions) - 1)

    for i, (x, y, z) in enumerate(positions):
        spline.points[i].co = (x, y, z, 1)

    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    return curve_obj
```


## Gmsh Mesh to Blender


```python
def gmsh_stl_to_blender(stl_path, name="FE_Mesh"):
    """Import Gmsh-exported STL into Blender."""
    try:
        bpy.ops.wm.stl_import(filepath=stl_path)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=stl_path)

    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj
```


## ParaView VTK to Blender


```python
def vtk_to_blender(vtk_path):
    """Import VTK file via meshio conversion to STL."""
    import meshio
    import tempfile
    import os

    mesh = meshio.read(vtk_path)
    tmp_stl = os.path.join(tempfile.gettempdir(), "vtk_import.stl")
    meshio.write(tmp_stl, mesh)

    try:
        bpy.ops.wm.stl_import(filepath=tmp_stl)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=tmp_stl)

    os.remove(tmp_stl)
    return bpy.context.selected_objects[0]
```
