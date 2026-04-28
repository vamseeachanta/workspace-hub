#!/usr/bin/env python3
"""Minimal headless Blender smoke render for workspace-hub issue #2270."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import bpy


def _args() -> argparse.Namespace:
    custom = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", required=True)
    return parser.parse_args(custom)


def _eevee_engine() -> str:
    # Blender 4.x uses BLENDER_EEVEE_NEXT; 3.x and 5.x use BLENDER_EEVEE.
    return "BLENDER_EEVEE_NEXT" if bpy.app.version[0] == 4 else "BLENDER_EEVEE"


def _write_metadata(path: Path, output: Path, file_size: int, engine: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""scene_name: cube-render
frame: 1
render_engine: {engine}
resolution:
  width: 320
  height: 240
image:
  format: PNG
  color_mode: RGBA
  output_file: {output}
  file_size_bytes: {file_size}
objects:
  - name: Smoke_Cube
    type: MESH
camera: Smoke_Camera
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = _args()
    output = Path(args.output)
    metadata = Path(args.metadata)
    output.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "Smoke_Cube"

    bpy.ops.object.light_add(type="AREA", location=(3, -4, 5))
    light = bpy.context.active_object
    light.name = "Smoke_Key_Light"
    light.data.energy = 350
    light.data.size = 4

    bpy.ops.object.camera_add(location=(4, -5, 3), rotation=(1.109319, 0.0, 0.674741))
    camera = bpy.context.active_object
    camera.name = "Smoke_Camera"
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    engine = _eevee_engine()
    scene.render.engine = engine
    scene.frame_set(1)
    scene.render.resolution_x = 320
    scene.render.resolution_y = 240
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(output)

    bpy.ops.render.render(write_still=True)
    file_size = output.stat().st_size
    _write_metadata(metadata, output, file_size, engine)
    print(f"Rendered cube-render frame 1: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
