---
name: blender-interface
description: AI interface skill for Blender 3D — headless CLI execution, Python bpy API, mesh import/export, rendering, and integration with engineering analysis workflows.
version: 1.0.0
updated: 2026-02-23
category: cad-engineering
triggers:
- Blender automation
- Blender Python
- bpy scripting
- 3D visualization
- Blender render
- mesh to Blender
- OrcaFlex visualization Blender
- headless Blender
- Blender CLI
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- freecad-automation
- gmsh-meshing
---
# Blender AI Interface Skill

AI agent interface for driving Blender 3D programmatically via CLI and Python bpy API. Covers headless execution, mesh import/export, material assignment, rendering, and integration with engineering analysis tools.

## 1. Input Generation

### Scene Setup via Python Script

```python
import bpy
import math

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create objects programmatically
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5, depth=10.0,
    location=(0, 0, 5),
    rotation=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "Riser_Section"
```

### Import Engineering Geometry

| Format | Operator | Notes |
|--------|----------|-------|
| STL | `bpy.ops.wm.stl_import(filepath=path)` | Blender 4.x; use `import_mesh.stl` for 3.x |
| OBJ | `bpy.ops.wm.obj_import(filepath=path)` | Blender 4.x; use `import_scene.obj` for 3.x |
| FBX | `bpy.ops.import_scene.fbx(filepath=path)` | Same across versions |
| PLY | `bpy.ops.wm.ply_import(filepath=path)` | Blender 4.x |
| GLTF | `bpy.ops.import_scene.gltf(filepath=path)` | Same across versions |
| DAE | `bpy.ops.wm.collada_import(filepath=path)` | Collada |

### Blender 3.x vs 4.x API Migration

| Operation | Blender 3.x | Blender 4.x |
|-----------|-------------|-------------|
| Import STL | `bpy.ops.import_mesh.stl()` | `bpy.ops.wm.stl_import()` |
| Import OBJ | `bpy.ops.import_scene.obj()` | `bpy.ops.wm.obj_import()` |
| Import PLY | `bpy.ops.import_mesh.ply()` | `bpy.ops.wm.ply_import()` |
| Export STL | `bpy.ops.export_mesh.stl()` | `bpy.ops.wm.stl_export()` |
| Export OBJ | `bpy.ops.export_scene.obj()` | `bpy.ops.wm.obj_export()` |
| BSDF Base Color | `node.inputs['Base Color']` | `node.inputs['Base Color']` (unchanged) |
| BSDF Roughness | `node.inputs['Roughness']` | `node.inputs['Roughness']` (unchanged) |
| BSDF Specular | `node.inputs['Specular']` | `node.inputs['Specular IOR Level']` |

### Material Assignment (Principled BSDF)

```python
def create_material(name, color_rgba, metallic=0.0, roughness=0.5):
    """Create a Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color_rgba  # (R, G, B, A)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

def assign_material(obj, material):
    """Assign material to object."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

# Engineering color scheme
steel_mat = create_material("Steel", (0.6, 0.6, 0.65, 1.0), metallic=0.8, roughness=0.3)
water_mat = create_material("Water", (0.1, 0.3, 0.6, 0.7), metallic=0.0, roughness=0.1)
seabed_mat = create_material("Seabed", (0.4, 0.35, 0.2, 1.0), metallic=0.0, roughness=0.9)
```

### Camera and Lighting Setup

```python
def setup_engineering_camera(target=(0, 0, 0), distance=20, elevation=30, azimuth=45):
    """Set up camera for engineering visualization."""
    elev_rad = math.radians(elevation)
    azim_rad = math.radians(azimuth)

    cam_x = target[0] + distance * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target[1] - distance * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target[2] + distance * math.sin(elev_rad)

    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.active_object
    camera.name = "Eng_Camera"

    # Point at target
    constraint = camera.constraints.new(type='TRACK_TO')
    empty = bpy.ops.object.empty_add(location=target)
    constraint.target = bpy.context.active_object
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.context.scene.camera = camera
    return camera

def setup_lighting():
    """Add 3-point lighting for engineering renders."""
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    key = bpy.context.active_object
    key.data.energy = 3.0

    bpy.ops.object.light_add(type='AREA', location=(-10, 5, 10))
    fill = bpy.context.active_object
    fill.data.energy = 1.5

    bpy.ops.object.light_add(type='POINT', location=(0, -15, 5))
    rim = bpy.context.active_object
    rim.data.energy = 2.0
```

### Render Settings Template

```python
def configure_render(engine='CYCLES', resolution=(1920, 1080), samples=128, gpu=True):
    """Configure render settings."""
    scene = bpy.context.scene
    scene.render.engine = engine  # 'CYCLES' or 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]

    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        if gpu:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type = 'CUDA'  # or 'OPTIX', 'HIP'
            prefs.get_devices()
            for device in prefs.devices:
                device.use = True
            scene.cycles.device = 'GPU'

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_depth = '16'
```

## 2. Execution

### CLI Headless Execution

```bash
# Run Python script headlessly (no GUI)
blender --background --python script.py

# Run with specific .blend file
blender model.blend --background --python script.py

# Render single frame
blender model.blend --background --render-output //renders/frame_ --render-frame 1

# Render animation (frames 1-250)
blender model.blend --background --render-output //renders/frame_ --render-anim

# Render specific frame range
blender model.blend --background --frame-start 1 --frame-end 100 --render-anim

# Pass custom arguments (after --)
blender --background --python script.py -- --input mesh.stl --output render.png
```

### CLI Flags Reference

| Flag | Purpose |
|------|---------|
| `--background` / `-b` | Run without GUI (headless) |
| `--python` / `-P` | Execute Python script |
| `--python-expr` | Execute Python expression inline |
| `--render-output` / `-o` | Set render output path |
| `--render-frame` / `-f` | Render single frame |
| `--render-anim` / `-a` | Render full animation |
| `--frame-start` / `-s` | Set start frame |
| `--frame-end` / `-e` | Set end frame |
| `--factory-startup` | Ignore user preferences |
| `--addons` | Enable specific addons |
| `--threads` | Set thread count |

### Accessing Custom Arguments in Script

```python
import sys

# Arguments after "--" are passed to the script
argv = sys.argv
if "--" in argv:
    custom_args = argv[argv.index("--") + 1:]
else:
    custom_args = []

# Parse with argparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args(custom_args)
```

### Complete Headless Render Pipeline

```python
#!/usr/bin/env python3
"""Headless Blender render script for engineering visualization."""
import bpy
import sys
import argparse

def parse_args():
    argv = sys.argv
    custom = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-stl", required=True)
    parser.add_argument("--output-png", required=True)
    parser.add_argument("--resolution", type=int, nargs=2, default=[1920, 1080])
    return parser.parse_args(custom)

def main():
    args = parse_args()

    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import geometry (Blender 4.x)
    try:
        bpy.ops.wm.stl_import(filepath=args.input_stl)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=args.input_stl)  # 3.x fallback

    obj = bpy.context.selected_objects[0]

    # Auto-center and scale
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)

    # Setup scene
    setup_engineering_camera(distance=max(obj.dimensions) * 2)
    setup_lighting()
    configure_render(resolution=tuple(args.resolution))

    # Render
    bpy.context.scene.render.filepath = args.output_png
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {args.output_png}")

if __name__ == "__main__":
    main()
```

## 3. Output Parsing

### Render Output Locations

```python
# Default render output
output_path = bpy.context.scene.render.filepath  # e.g., "//renders/frame_"

# Actual rendered files follow pattern:
# //renders/frame_0001.png, frame_0002.png, etc.
```

### Export Geometry

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

### Extract Scene Statistics

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

### Parse Render Console Output

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

## 4. Failure Diagnosis

### Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'NoneType' has no attribute 'select_set'` | No active object after operation | Check `bpy.context.selected_objects` before accessing |
| `RuntimeError: Operator bpy.ops.wm.stl_import not found` | Blender version mismatch (3.x vs 4.x) | Use version-gated import (see migration table) |
| `CUDA error: out of memory` | GPU memory exhausted during Cycles render | Reduce tile size, lower samples, or use CPU fallback |
| `Segmentation fault` in headless | Missing display server | Set `DISPLAY=:0` or use `xvfb-run blender --background` |
| `bpy.ops.render.render(): Error, no camera` | No camera in scene or not set as active | `bpy.context.scene.camera = cam_object` |
| `Cannot read file: ...blend` | Blend file version newer than Blender | Use matching Blender version or save backward-compatible |
| `operator returned {'CANCELLED'}` | Operation context incorrect | Ensure correct context override or use `with bpy.context.temp_override()` |

### Diagnostic Function

```python
def diagnose_blender_env():
    """Check Blender environment for common issues."""
    import bpy
    diag = {"version": bpy.app.version_string, "issues": [], "info": []}

    # Check version
    major = bpy.app.version[0]
    diag["info"].append(f"Blender {bpy.app.version_string}")
    if major < 3:
        diag["issues"].append("Blender < 3.0 — many operators unavailable")

    # Check GPU
    if bpy.context.preferences.addons.get('cycles'):
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.get_devices()
        gpu_devices = [d for d in prefs.devices if d.type != 'CPU']
        if gpu_devices:
            for d in gpu_devices:
                diag["info"].append(f"GPU: {d.name} ({d.type})")
        else:
            diag["issues"].append("No GPU detected — Cycles will use CPU only")

    # Check camera
    if not bpy.context.scene.camera:
        diag["issues"].append("No active camera — render will fail")

    # Check for orphaned data
    orphans = len([m for m in bpy.data.meshes if m.users == 0])
    if orphans > 10:
        diag["issues"].append(f"{orphans} orphaned meshes — call bpy.ops.outliner.orphans_purge()")

    return diag
```

### Headless Display Fix

```bash
# If Blender crashes with display errors on a headless server:
# Option 1: Use xvfb (X Virtual Frame Buffer)
xvfb-run -a blender --background --python script.py

# Option 2: Set EGL for GPU rendering without display
export DISPLAY=:0
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
blender --background --python script.py
```

## 5. Validation

### Mesh Quality Checks

```python
def validate_imported_mesh(obj):
    """Validate mesh quality after import."""
    import bmesh
    checks = {"passed": True, "issues": []}

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Check for non-manifold edges
    non_manifold = [e for e in bm.edges if not e.is_manifold]
    if non_manifold:
        checks["issues"].append(f"{len(non_manifold)} non-manifold edges")

    # Check for loose vertices
    loose = [v for v in bm.verts if not v.link_edges]
    if loose:
        checks["issues"].append(f"{len(loose)} loose vertices")

    # Check for degenerate faces (zero area)
    degen = [f for f in bm.faces if f.calc_area() < 1e-8]
    if degen:
        checks["issues"].append(f"{len(degen)} degenerate faces")

    # Check normals consistency
    bm.normal_update()

    bm.free()

    checks["vertex_count"] = len(mesh.vertices)
    checks["face_count"] = len(mesh.polygons)
    checks["passed"] = len(checks["issues"]) == 0
    return checks
```

### Render Validation

```python
import os

def validate_render_output(output_path, expected_frames=1):
    """Validate render output exists and is reasonable."""
    checks = {"passed": True, "issues": []}

    if not os.path.exists(output_path):
        checks["issues"].append(f"Output not found: {output_path}")
        checks["passed"] = False
        return checks

    size_bytes = os.path.getsize(output_path)
    if size_bytes < 1000:
        checks["issues"].append(f"Output suspiciously small: {size_bytes} bytes (likely blank)")
        checks["passed"] = False

    # Check image dimensions (requires PIL)
    try:
        from PIL import Image
        img = Image.open(output_path)
        checks["resolution"] = img.size
        checks["mode"] = img.mode

        # Check if image is all-black (failed render)
        extrema = img.convert("L").getextrema()
        if extrema == (0, 0):
            checks["issues"].append("Render is all-black — check lighting and materials")
            checks["passed"] = False
    except ImportError:
        checks["issues"].append("PIL not available — skipping image content check")

    return checks
```

### Scale and Units Check

```python
def validate_engineering_scale(obj, expected_max_dim_m=500):
    """Check that imported geometry is at engineering scale (meters)."""
    dims = obj.dimensions
    max_dim = max(dims)

    if max_dim < 0.001:
        return {"issue": f"Max dimension {max_dim:.6f}m — likely in mm, scale by 1000"}
    if max_dim > expected_max_dim_m * 10:
        return {"issue": f"Max dimension {max_dim:.1f}m — likely wrong units"}
    return {"ok": True, "dimensions_m": tuple(dims)}
```

## 6. Integration

### OrcaFlex Results to Blender Visualization

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

### Gmsh Mesh to Blender

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

### ParaView VTK to Blender

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

## Related Skills

- [freecad-automation](../freecad-automation/SKILL.md) - Parametric CAD geometry
- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Mesh generation for analysis
- [paraview-interface](../../cfd/paraview/SKILL.md) - Scientific visualization

## References

- Blender Python API: https://docs.blender.org/api/current/
- Blender CLI Reference: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html

---

## Version History

- **1.0.0** (2026-02-23): Initial full interface skill covering CLI execution, bpy API, 3.x/4.x migration, rendering, mesh validation, and engineering integration.
