---
name: paraview-interface-common-failures
description: 'Sub-skill of paraview-interface: Common Failures (+1).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Failures (+1)

## Common Failures


| Error | Cause | Fix |
|-------|-------|-----|
| `ERROR: In vtkOpenFOAMReader` | Missing `case.foam` or wrong path | Create empty `.foam` file in case root |
| `ERROR: no mesh regions selected` | Reader has no regions enabled | Set `reader.MeshRegions = ['internalMesh']` |
| `Cannot render: display not available` | No X display on headless server | Use `pvbatch` or `--force-offscreen-rendering` |
| `Segfault in pvbatch` | Mesa/GPU driver conflict | Try `--mesa` flag or update drivers |
| `SIGSEGV in vtkSMParaViewPipelineControllerWithRendering::New()` | ParaView 5.11 on Ubuntu 24.04 + NVIDIA 580 | Use Snap/conda ParaView install, or upgrade to ParaView >= 5.12. VTK layer (pip) works as fallback for data operations |
| `SaveScreenshot: view size 0x0` | ViewSize not set | Set `view.ViewSize = [1920, 1080]` before save |
| `KeyError: 'U'` | Array not loaded by reader | Check `reader.CellArrays` or `reader.PointArrays` |
| `Empty output from PlotOverLine` | Line doesn't intersect data | Verify Point1/Point2 are within data bounds |
| `paraview.simple not found` | Wrong Python interpreter | Use `pvpython` or `pvbatch`, not system Python |


## Diagnostic Script


```python
from paraview.simple import *

def diagnose_paraview_setup():
    """Check ParaView environment and data loading."""
    import paraview
    diag = {"version": paraview.compatibility.GetVersion(), "issues": []}

    # Check rendering
    view = GetActiveViewOrCreate('RenderView')
    if view.ViewSize == [0, 0]:
        diag["issues"].append("ViewSize is 0x0 — set explicitly before rendering")

    # Check GPU rendering
    try:
        from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer
        diag["rendering"] = "OpenGL (hardware)"
    except ImportError:
        diag["rendering"] = "Mesa (software)"
        diag["issues"].append("Software rendering — renders will be slow")

    return diag

def diagnose_openfoam_case(case_path):
    """Diagnose OpenFOAM case loading issues."""
    import os
    diag = {"issues": []}

    foam_file = os.path.join(case_path, os.path.basename(case_path) + '.foam')
    if not os.path.exists(foam_file):
        # Try any .foam file
        foam_files = [f for f in os.listdir(case_path) if f.endswith('.foam')]
        if not foam_files:
            diag["issues"].append(f"No .foam file in {case_path} — create with: touch case.foam")
            return diag
        foam_file = os.path.join(case_path, foam_files[0])

    reader = OpenFOAMReader(FileName=foam_file)
    reader.UpdatePipeline()

    if not reader.MeshRegions.Available:
        diag["issues"].append("No mesh regions found — check polyMesh/")

    if not reader.CellArrays.Available:
        diag["issues"].append("No cell arrays found — simulation may not have run")

    time_steps = reader.TimestepValues
    diag["time_steps"] = len(time_steps)
    if len(time_steps) == 0:
        diag["issues"].append("No time steps — check time directories")

    return diag
```
