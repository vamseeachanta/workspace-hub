---
name: blender-interface-scene-setup-via-python-script
description: 'Sub-skill of blender-interface: Scene Setup via Python Script (+5).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Scene Setup via Python Script (+5)

## Scene Setup via Python Script


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


## Import Engineering Geometry


| Format | Operator | Notes |
|--------|----------|-------|
| STL | `bpy.ops.wm.stl_import(filepath=path)` | Blender 4.x; use `import_mesh.stl` for 3.x |
| OBJ | `bpy.ops.wm.obj_import(filepath=path)` | Blender 4.x; use `import_scene.obj` for 3.x |
| FBX | `bpy.ops.import_scene.fbx(filepath=path)` | Same across versions |
| PLY | `bpy.ops.wm.ply_import(filepath=path)` | Blender 4.x |
| GLTF | `bpy.ops.import_scene.gltf(filepath=path)` | Same across versions |
| DAE | `bpy.ops.wm.collada_import(filepath=path)` | Collada |


## Blender 3.x / 4.x / 5.x API Migration


| Operation | Blender 3.x | Blender 4.x | Blender 5.x |
|-----------|-------------|-------------|-------------|
| Import STL | `bpy.ops.import_mesh.stl()` | `bpy.ops.wm.stl_import()` | same as 4.x |
| Import OBJ | `bpy.ops.import_scene.obj()` | `bpy.ops.wm.obj_import()` | same as 4.x |
| Import PLY | `bpy.ops.import_mesh.ply()` | `bpy.ops.wm.ply_import()` | same as 4.x |
| Export STL | `bpy.ops.export_mesh.stl()` | `bpy.ops.wm.stl_export()` | same as 4.x |
| Export OBJ | `bpy.ops.export_scene.obj()` | `bpy.ops.wm.obj_export()` | same as 4.x |
| BSDF Specular | `node.inputs['Specular']` | `node.inputs['Specular IOR Level']` | same as 4.x |
| EEVEE engine | `'BLENDER_EEVEE'` | `'BLENDER_EEVEE_NEXT'` | `'BLENDER_EEVEE'` (reverted) |
| `use_nodes` | required | required | deprecated (always on) |


## Material Assignment (Principled BSDF)


```python
def create_material(name, color_rgba, metallic=0.0, roughness=0.5):
    """Create a Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version[0] < 5:  # use_nodes deprecated in 5.x (always on)
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


## Camera and Lighting Setup


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


## Render Settings Template


```python
def configure_render(engine='CYCLES', resolution=(1920, 1080), samples=128, gpu=True):
    """Configure render settings."""
    scene = bpy.context.scene
    # EEVEE enum name changed across versions:
    #   3.x: 'BLENDER_EEVEE', 4.x: 'BLENDER_EEVEE_NEXT', 5.x: 'BLENDER_EEVEE'
    if engine in ('EEVEE', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version[0] == 4 else 'BLENDER_EEVEE'
    scene.render.engine = engine  # 'CYCLES' or resolved EEVEE name
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
