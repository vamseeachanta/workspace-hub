---
name: blender-interface-common-failures
description: 'Sub-skill of blender-interface: Common Failures (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Failures (+2)

## Common Failures


| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'NoneType' has no attribute 'select_set'` | No active object after operation | Check `bpy.context.selected_objects` before accessing |
| `RuntimeError: Operator bpy.ops.wm.stl_import not found` | Blender version mismatch (3.x vs 4.x) | Use version-gated import (see migration table) |
| `CUDA error: out of memory` | GPU memory exhausted during Cycles render | Reduce tile size, lower samples, or use CPU fallback |
| `Segmentation fault` in headless | Missing display server | Set `DISPLAY=:0` or use `xvfb-run blender --background` |
| `bpy.ops.render.render(): Error, no camera` | No camera in scene or not set as active | `bpy.context.scene.camera = cam_object` |
| `Cannot read file: ...blend` | Blend file version newer than Blender | Use matching Blender version or save backward-compatible |
| `operator returned {'CANCELLED'}` | Operation context incorrect | Ensure correct context override or use `with bpy.context.temp_override()` |
| `enum "BLENDER_EEVEE_NEXT" not found` | Blender 5.x reverted EEVEE enum name | Use version check: `'BLENDER_EEVEE_NEXT' if bpy.app.version[0]==4 else 'BLENDER_EEVEE'` |
| `DeprecationWarning: 'Material.use_nodes'` | Blender 5.x always enables nodes | Guard with `if bpy.app.version[0] < 5: mat.use_nodes = True` |


## Diagnostic Function


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


## Headless Display Fix


```bash
# If Blender crashes with display errors on a headless server:
# Option 1: Use xvfb (X Virtual Frame Buffer)
xvfb-run -a blender --background --python script.py

# Option 2: Set EGL for GPU rendering without display
export DISPLAY=:0
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
blender --background --python script.py
```
