---
name: blender-interface-render-output-locations
description: 'Sub-skill of blender-interface: Render Output Locations (+3).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Render Output Locations (+3)

## Render Output Locations


```python
# Default render output
output_path = bpy.context.scene.render.filepath  # e.g., "//renders/frame_"

# Actual rendered files follow pattern:
# //renders/frame_0001.png, frame_0002.png, etc.
```


## Export Geometry


```python
def export_mesh(obj, filepath, format='STL'):
    """Export selected object to file."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    exporters = {
        'STL': lambda: bpy.ops.wm.stl_export(filepath=filepath),
        'OBJ': lambda: bpy.ops.wm.obj_export(filepath=filepath),
        'PLY': lambda: bpy.ops.wm.ply_export(filepath=filepath),
        'FBX': lambda: bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True),
        'GLTF': lambda: bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True),
    }

    try:
        exporters[format]()
    except AttributeError:
        # Blender 3.x fallback
        fallbacks = {
            'STL': lambda: bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True),
            'OBJ': lambda: bpy.ops.export_scene.obj(filepath=filepath, use_selection=True),
        }
        fallbacks[format]()
```


## Extract Scene Statistics


```python
def get_scene_stats():
    """Extract scene statistics for validation."""
    stats = {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "materials": len(bpy.data.materials),
        "total_vertices": 0,
        "total_faces": 0,
    }
    for mesh in bpy.data.meshes:
        stats["total_vertices"] += len(mesh.vertices)
        stats["total_faces"] += len(mesh.polygons)
    return stats
```


## Parse Render Console Output


```python
import re

def parse_render_log(log_text):
    """Parse Blender render console output."""
    results = {"frames": [], "total_time": None, "errors": []}

    for line in log_text.splitlines():
        # Frame render time: "Fra:1 Mem:256.00M (Peak 512.00M) | Time:00:01.23"
        frame_match = re.search(
            r'Fra:(\d+)\s+Mem:([\d.]+)M.*Time:([\d:.]+)', line
        )
        if frame_match:
            results["frames"].append({
                "frame": int(frame_match.group(1)),
                "memory_mb": float(frame_match.group(2)),
                "time": frame_match.group(3),
            })

        # Errors
        if "Error" in line or "error" in line:
            results["errors"].append(line.strip())

    return results
```
