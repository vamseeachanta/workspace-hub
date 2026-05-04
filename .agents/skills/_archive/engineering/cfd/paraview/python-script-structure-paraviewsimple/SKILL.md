---
name: paraview-interface-python-script-structure-paraviewsimple
description: 'Sub-skill of paraview-interface: Python Script Structure (paraview.simple)
  (+5).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Python Script Structure (paraview.simple) (+5)

## Python Script Structure (paraview.simple)


```python
from paraview.simple import *

# Disable automatic rendering for batch performance
paraview.simple._DisableFirstRenderCameraReset()

# Load data source
reader = OpenFOAMReader(registrationName='case', FileName='case.foam')
reader.MeshRegions = ['internalMesh']
reader.CellArrays = ['U', 'p']

# Set time step
animationScene = GetAnimationScene()
animationScene.UpdateAnimationUsingDataTimeSteps()
animationScene.AnimationTime = reader.TimestepValues[-1]  # Last time step

# Create render view
renderView = GetActiveViewOrCreate('RenderView')
renderView.ViewSize = [1920, 1080]
```


## Loading Different Data Formats


| Format | Reader | Key Parameters |
|--------|--------|----------------|
| OpenFOAM | `OpenFOAMReader(FileName='case.foam')` | `MeshRegions`, `CellArrays`, `SkipZeroTime` |
| VTK | `LegacyVTKReader(FileNames=['file.vtk'])` | Direct read |
| VTU | `XMLUnstructuredGridReader(FileName=['file.vtu'])` | Direct read |
| CSV | `CSVReader(FileName=['data.csv'])` | `HaveHeaders`, `DetectNumericColumns` |
| EnSight | `EnSightReader(CaseFileName='file.case')` | `PointArrays` |
| STL | `STLReader(FileNames=['mesh.stl'])` | Surface only |


## OpenFOAM .foam File


Create a `.foam` trigger file in the case directory:

```bash
# Empty file triggers OpenFOAM reader
touch /path/to/case/case.foam
```


## Color Map Configuration


```python
def setup_color_map(display, array_name, component=None, preset='Cool to Warm'):
    """Configure color mapping for a display."""
    ColorBy(display, ('POINTS', array_name, component) if component else ('POINTS', array_name))

    color_tf = GetColorTransferFunction(array_name)
    opacity_tf = GetOpacityTransferFunction(array_name)

    # Apply preset
    color_tf.ApplyPreset(preset, True)

    # Auto-rescale to data range
    color_tf.RescaleTransferFunction(*display.RescaleTransferFunctionToDataRange(True))

    # Show color bar
    display.SetScalarBarVisibility(GetActiveView(), True)

    return color_tf
```


## Common Color Map Presets


| Preset | Use Case |
|--------|----------|
| `Cool to Warm` | Diverging data (pressure, temperature) |
| `Viridis (matplotlib)` | Sequential data (velocity magnitude) |
| `Rainbow Uniform` | General purpose |
| `Blue to Red Rainbow` | Temperature fields |
| `Jet` | Legacy CFD visualization |
| `Black-Body Radiation` | Heat transfer |


## Camera Setup


```python
def set_camera(view, position, focal_point, up=(0, 0, 1)):
    """Set camera position and orientation."""
    view.CameraPosition = position
    view.CameraFocalPoint = focal_point
    view.CameraViewUp = up
    view.CameraParallelScale = 1.0
    Render()

def set_isometric_view(view):
    """Standard isometric engineering view."""
    view.ResetCamera()
    view.CameraPosition = [1, 1, 1]
    view.CameraFocalPoint = [0, 0, 0]
    view.CameraViewUp = [0, 0, 1]
    view.ResetCamera()
    Render()
```
