#!/usr/bin/env python3
"""Minimal Blender headless smoke render for issue #2270.

Intended invocation:
    blender -b --python scripts/blender/smoke-render.py -- --output /tmp/smoke-render.png

The script creates a default cube scene, adds a camera and light, and writes a single PNG frame.
It is deliberately dependency-light so the baseline validator can run on dev-secondary without project data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a minimal cube PNG in Blender headless mode.")
    parser.add_argument("--output", required=True, help="PNG output path")
    argv = sys.argv[1:]
    if argv and argv[0] == "--":
        argv = argv[1:]
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    import bpy  # type: ignore[import-not-found]

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
    cube = bpy.context.object
    cube.name = "baseline_cube"

    bpy.ops.object.light_add(type="AREA", location=(0.0, -3.0, 4.0))
    light = bpy.context.object
    light.name = "baseline_area_light"
    light.data.energy = 350
    light.data.size = 5

    bpy.ops.object.camera_add(location=(4.0, -5.0, 3.0), rotation=(1.1, 0.0, 0.68))
    bpy.context.scene.camera = bpy.context.object

    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.context.scene, "eevee") else "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 320
    bpy.context.scene.render.resolution_y = 240
    bpy.context.scene.render.filepath = str(output)
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
