---
name: blender-interface-cli-headless-execution
description: 'Sub-skill of blender-interface: CLI Headless Execution (+3).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Headless Execution (+3)

## CLI Headless Execution


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


## CLI Flags Reference


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


## Accessing Custom Arguments in Script


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


## Complete Headless Render Pipeline


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
