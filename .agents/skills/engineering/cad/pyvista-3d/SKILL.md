---
name: pyvista-3d
description: "AI interface skill for PyVista 3D visualization --- VTK wrapper for mesh
  rendering, STL/OBJ/VTK I/O, scalar coloring, offscreen rendering, and engineering
  analysis post-processing."
type: reference
version: 1.0.0
updated: 2026-03-31
category: engineering
triggers:
- PyVista
- pyvista
- 3D mesh visualization
- VTK visualization Python
- offscreen 3D rendering
- mesh quality visualization
- point cloud rendering
- STL visualization
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- blender-interface
- paraview-interface
- gmsh-meshing
tags:
- pyvista
- vtk
- 3d
- mesh
- visualization
scripts_exempt: true
---

# PyVista 3D Visualization

## Overview

PyVista (MIT, 3.6k stars) is a Pythonic wrapper around VTK for 3D spatial data visualization. It provides a streamlined API for rendering meshes, point clouds, STL/OBJ geometry, and scalar fields without low-level VTK boilerplate.

## Key Capabilities

| Feature | Details |
|---------|---------|
| Mesh rendering | Surface, wireframe, point cloud, volume rendering |
| Scalar coloring | Map data arrays to colormaps (coolwarm, viridis, plasma, etc.) |
| File I/O | STL, OBJ, PLY, VTK, VTP --- plus all meshio-supported formats |
| Offscreen rendering | `off_screen=True` for headless/CI environments |
| GPU acceleration | Uses OpenGL via VTK; works with NVIDIA GPUs |
| Jupyter integration | Interactive 3D in notebooks via trame |
| Mesh quality | Built-in quality metrics (scaled Jacobian, aspect ratio, etc.) |
| Engineering use | Pipe geometry, FEA results, terrain, bathymetry, point clouds |

## Quick Start

```python
import pyvista as pv

# Load and render a mesh
mesh = pv.read("geometry.stl")
mesh.plot(scalars="pressure", cmap="coolwarm")

# Offscreen rendering
plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))
plotter.add_mesh(mesh, scalars="depth", cmap="viridis")
plotter.screenshot("output.png")
plotter.close()

# Pipe geometry from spline
import numpy as np
t = np.linspace(0, 10, 50)
points = np.column_stack((t, np.zeros_like(t), np.cosh((t-5)/5)))
spline = pv.Spline(points, n_points=200)
pipe = spline.tube(radius=0.15, n_sides=20)
pipe.plot()
```

## Environment

- **Python**: >= 3.10
- **Tested**: PyVista 0.47.1, VTK 9.6.0, NVIDIA GTX 750 Ti
- **Headless**: Set `PYVISTA_OFF_SCREEN=true` or use `off_screen=True` in Plotter

## Known Issues

- `cell_quality()` segfaults on tube meshes with VTK 9.6; use deprecated `compute_cell_quality()` until PyVista 0.48+
- First render in a session takes 500-700ms (OpenGL context init); subsequent renders are 35ms

## Related Skills

- [blender-interface](../blender/SKILL.md) --- Full 3D scene composition and rendering
- [gmsh-meshing](../gmsh-meshing/SKILL.md) --- Mesh generation for analysis
- [freecad-automation](../freecad-automation/SKILL.md) --- Parametric CAD geometry

## References

- PyVista docs: https://docs.pyvista.org/
- PyVista GitHub: https://github.com/pyvista/pyvista
- Evaluation script: `scripts/examples/pyvista_3d_evaluation.py`
