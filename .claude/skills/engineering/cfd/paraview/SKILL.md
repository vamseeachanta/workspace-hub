---
name: paraview-interface
description: AI interface skill for ParaView scientific visualization — pvpython/pvbatch CLI execution, paraview.simple API, filter pipelines, OpenFOAM integration, and automated image/data export.
version: 1.1.0
updated: 2026-02-24
category: cfd-engineering
triggers:
- ParaView automation
- pvpython
- pvbatch
- ParaView Python
- OpenFOAM visualization
- VTK visualization
- CFD post-processing
- paraview.simple
- ParaView filter
- ParaView screenshot
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- openfoam
- blender-interface
---
# ParaView AI Interface Skill

AI agent interface for driving ParaView programmatically via pvpython/pvbatch and the paraview.simple API. Covers OpenFOAM result loading, filter pipelines, data extraction, and automated image/animation export.

## 1. Input Generation

### Python Script Structure (paraview.simple)

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

### Loading Different Data Formats

| Format | Reader | Key Parameters |
|--------|--------|----------------|
| OpenFOAM | `OpenFOAMReader(FileName='case.foam')` | `MeshRegions`, `CellArrays`, `SkipZeroTime` |
| VTK | `LegacyVTKReader(FileNames=['file.vtk'])` | Direct read |
| VTU | `XMLUnstructuredGridReader(FileName=['file.vtu'])` | Direct read |
| CSV | `CSVReader(FileName=['data.csv'])` | `HaveHeaders`, `DetectNumericColumns` |
| EnSight | `EnSightReader(CaseFileName='file.case')` | `PointArrays` |
| STL | `STLReader(FileNames=['mesh.stl'])` | Surface only |

### OpenFOAM .foam File

Create a `.foam` trigger file in the case directory:

```bash
# Empty file triggers OpenFOAM reader
touch /path/to/case/case.foam
```

### Color Map Configuration

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

### Common Color Map Presets

| Preset | Use Case |
|--------|----------|
| `Cool to Warm` | Diverging data (pressure, temperature) |
| `Viridis (matplotlib)` | Sequential data (velocity magnitude) |
| `Rainbow Uniform` | General purpose |
| `Blue to Red Rainbow` | Temperature fields |
| `Jet` | Legacy CFD visualization |
| `Black-Body Radiation` | Heat transfer |

### Camera Setup

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

## 2. Execution

### CLI Execution

```bash
# Run ParaView Python script (with GUI libraries, offscreen)
pvpython script.py

# Run in pure batch mode (no GUI libraries needed)
pvbatch script.py

# Parallel execution with MPI
mpirun -np 4 pvbatch script.py

# With offscreen rendering (mesa)
pvbatch --force-offscreen-rendering script.py

# Specify specific mesa/EGL
DISPLAY=:0 pvpython script.py
```

### pvpython vs pvbatch

| Feature | pvpython | pvbatch |
|---------|----------|---------|
| GUI available | Yes (can show windows) | No (headless only) |
| MPI parallel | No | Yes |
| Offscreen | Via `--force-offscreen-rendering` | Default |
| Use case | Interactive scripts, debugging | Production batch jobs |

### CLI Flags

| Flag | Purpose |
|------|---------|
| `--force-offscreen-rendering` | Force offscreen (no display needed) |
| `--mesa` | Use Mesa software rendering |
| `-dr` | Disable registry (ignore saved settings) |
| `--state=file.pvsm` | Load ParaView state file |
| `--data=file.vtk` | Load data file |

### Environment Setup

```bash
# Typical ParaView environment (installed via package manager)
export PATH=/usr/bin:$PATH  # pvpython, pvbatch in standard path

# Or from tarball installation
export PARAVIEW_HOME=/opt/ParaView-5.12
export PATH=$PARAVIEW_HOME/bin:$PATH
export LD_LIBRARY_PATH=$PARAVIEW_HOME/lib:$LD_LIBRARY_PATH
```

## 3. Output Parsing

### Save Screenshots

```python
def save_screenshot(view, filepath, resolution=(1920, 1080), transparent=False):
    """Save render view as image."""
    view.ViewSize = list(resolution)
    SaveScreenshot(
        filepath, view,
        ImageResolution=list(resolution),
        TransparentBackground=1 if transparent else 0,
    )
    print(f"Saved: {filepath}")
```

### Save Animation

```python
def save_animation(view, output_dir, prefix='frame', resolution=(1920, 1080)):
    """Save animation frames as image sequence."""
    view.ViewSize = list(resolution)
    SaveAnimation(
        f'{output_dir}/{prefix}.png', view,
        ImageResolution=list(resolution),
        FrameWindow=[0, GetAnimationScene().NumberOfFrames - 1],
    )
```

### Extract Data to CSV

```python
def extract_line_data(source, point1, point2, num_points=100, output_csv='line_data.csv'):
    """Extract data along a line (plot over line)."""
    plot_line = PlotOverLine(registrationName='LineProbe', Input=source)
    plot_line.Point1 = point1
    plot_line.Point2 = point2
    plot_line.Resolution = num_points

    # Save to CSV
    SaveData(output_csv, proxy=plot_line,
             ChooseArraysToWrite=0,
             Precision=8)
    print(f"Line data saved: {output_csv}")
    return plot_line

def extract_surface_integral(source, array_name, output_csv='surface_data.csv'):
    """Integrate variable over a surface."""
    integrate = IntegrateVariables(registrationName='Integral', Input=source)
    SaveData(output_csv, proxy=integrate)
    return integrate
```

### Parse CSV Output

```python
import csv

def parse_paraview_csv(csv_path):
    """Parse ParaView CSV export."""
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key, value in row.items():
                key = key.strip().strip('"')
                if key not in data:
                    data[key] = []
                try:
                    data[key].append(float(value))
                except ValueError:
                    data[key].append(value)
    return data
```

### Common Filter Pipeline

```python
def build_standard_cfd_pipeline(reader):
    """Build standard CFD visualization pipeline."""
    results = {}

    # Velocity magnitude slice
    slice_filter = Slice(registrationName='ZSlice', Input=reader)
    slice_filter.SliceType = 'Plane'
    slice_filter.SliceType.Origin = [0, 0, 0]
    slice_filter.SliceType.Normal = [0, 0, 1]
    results['z_slice'] = slice_filter

    # Streamlines
    stream = StreamTracer(registrationName='Streams', Input=reader)
    stream.SeedType = 'Line'
    stream.SeedType.Point1 = [-1, -1, 0]
    stream.SeedType.Point2 = [-1, 1, 0]
    stream.SeedType.Resolution = 50
    stream.MaximumStreamlineLength = 20.0
    results['streamlines'] = stream

    # Contour (iso-surface)
    contour = Contour(registrationName='PressureIso', Input=reader)
    contour.ContourBy = ['POINTS', 'p']
    contour.Isosurfaces = [0.0]
    results['pressure_contour'] = contour

    # Calculator (derived quantity)
    calc = Calculator(registrationName='VelMag', Input=reader)
    calc.Function = 'mag(U)'
    calc.ResultArrayName = 'VelocityMagnitude'
    results['vel_magnitude'] = calc

    return results
```

### Filter Reference

| Filter | Purpose | Key Parameters |
|--------|---------|----------------|
| `Slice` | Cut plane through volume | `SliceType`, `Origin`, `Normal` |
| `Contour` | Iso-surface extraction | `ContourBy`, `Isosurfaces` |
| `StreamTracer` | Flow streamlines | `SeedType`, `MaximumStreamlineLength` |
| `Calculator` | Derived quantities | `Function`, `ResultArrayName` |
| `Clip` | Remove half of domain | `ClipType`, `InsideOut` |
| `Threshold` | Filter by value range | `ThresholdRange`, `Scalars` |
| `Glyph` | Vector arrows | `GlyphType`, `ScaleFactor` |
| `WarpByVector` | Deform mesh by vector | `Vectors`, `ScaleFactor` |
| `ExtractSurface` | Volume to surface | — |
| `CellDatatoPointData` | Interpolate cell→point | — |
| `IntegrateVariables` | Area/volume integrals | — |
| `PlotOverLine` | Line probe for XY plots | `Point1`, `Point2`, `Resolution` |
| `TemporalStatistics` | Time-averaged fields | `ComputeAverage`, `ComputeMinimum` |

## 4. Failure Diagnosis

### Common Failures

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

### Diagnostic Script

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

## 5. Validation

### Verify Data Range

```python
def validate_data_ranges(source, expected_ranges):
    """Validate that data arrays are within expected ranges.

    Args:
        source: ParaView source/filter
        expected_ranges: dict of {'array_name': (min, max)}
    """
    source.UpdatePipeline()
    data_info = source.GetDataInformation()
    checks = {"passed": True, "issues": []}

    for name, (exp_min, exp_max) in expected_ranges.items():
        array_info = data_info.GetArrayInformation(name, 0)  # 0=point, 1=cell
        if not array_info:
            array_info = data_info.GetArrayInformation(name, 1)
        if not array_info:
            checks["issues"].append(f"Array '{name}' not found")
            checks["passed"] = False
            continue

        data_range = array_info.GetComponentRange(0)
        if data_range[0] < exp_min * 0.5 or data_range[1] > exp_max * 2.0:
            checks["issues"].append(
                f"{name}: range [{data_range[0]:.3f}, {data_range[1]:.3f}] "
                f"outside expected [{exp_min}, {exp_max}]"
            )
            checks["passed"] = False

    return checks

# Example: validate typical CFD ranges
validate_data_ranges(reader, {
    'p': (-1e5, 1e5),       # Pressure (Pa, relative)
    'U': (-50, 50),          # Velocity (m/s)
    'k': (0, 100),           # Turbulent kinetic energy
    'omega': (0, 1e6),       # Specific dissipation rate
})
```

### Verify Screenshot Output

```python
import os

def validate_screenshots(output_dir, expected_count=1, min_size_kb=10):
    """Validate that screenshots were generated correctly."""
    checks = {"passed": True, "issues": [], "files": []}

    images = [f for f in os.listdir(output_dir)
              if f.endswith(('.png', '.jpg', '.tiff'))]

    if len(images) < expected_count:
        checks["issues"].append(
            f"Expected {expected_count} images, found {len(images)}"
        )
        checks["passed"] = False

    for img in images:
        path = os.path.join(output_dir, img)
        size_kb = os.path.getsize(path) / 1024
        checks["files"].append({"name": img, "size_kb": size_kb})
        if size_kb < min_size_kb:
            checks["issues"].append(f"{img}: {size_kb:.1f} KB — likely blank render")
            checks["passed"] = False

    return checks
```

### OpenFOAM Case Completeness Check

```python
def validate_openfoam_for_paraview(case_dir):
    """Check that OpenFOAM case is ready for ParaView visualization."""
    import os
    checks = {"passed": True, "issues": []}

    # Check polyMesh exists
    polymesh = os.path.join(case_dir, 'constant', 'polyMesh')
    if not os.path.isdir(polymesh):
        checks["issues"].append("No constant/polyMesh/ — mesh not generated")
        checks["passed"] = False

    # Check time directories
    time_dirs = [d for d in os.listdir(case_dir)
                 if d.replace('.', '').isdigit() and d != '0']
    if not time_dirs:
        checks["issues"].append("No result time directories — simulation not run")
        checks["passed"] = False
    else:
        checks["time_dirs"] = len(time_dirs)

    # Check for .foam file
    foam_files = [f for f in os.listdir(case_dir) if f.endswith('.foam')]
    if not foam_files:
        checks["issues"].append("No .foam file — create with: touch case.foam")

    return checks
```

## 6. Integration

### OpenFOAM to ParaView Pipeline

```python
"""Complete OpenFOAM post-processing pipeline."""
from paraview.simple import *

def openfoam_to_images(case_dir, output_dir, fields=['U', 'p']):
    """Generate standard visualization images from OpenFOAM case."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Create .foam file if needed
    foam_file = os.path.join(case_dir, 'case.foam')
    if not os.path.exists(foam_file):
        open(foam_file, 'w').close()

    # Load case
    reader = OpenFOAMReader(FileName=foam_file)
    reader.MeshRegions = ['internalMesh']
    reader.CellArrays = fields
    reader.SkipZeroTime = 1

    # Go to last time step
    anim = GetAnimationScene()
    anim.UpdateAnimationUsingDataTimeSteps()
    anim.AnimationTime = reader.TimestepValues[-1]

    view = GetActiveViewOrCreate('RenderView')
    view.ViewSize = [1920, 1080]
    view.Background = [1, 1, 1]  # White background

    for field in fields:
        display = Show(reader, view)
        ColorBy(display, ('POINTS', field))
        display.SetScalarBarVisibility(view, True)
        view.ResetCamera()
        Render()

        SaveScreenshot(
            os.path.join(output_dir, f'{field}_final.png'),
            view, ImageResolution=[1920, 1080]
        )
        Hide(reader, view)

    return output_dir
```

### VTK Export for Blender

```python
def export_surface_for_blender(source, output_stl):
    """Export surface mesh as STL for Blender import."""
    surface = ExtractSurface(Input=source)
    triangulate = Triangulate(Input=surface)
    SaveData(output_stl, proxy=triangulate)
    print(f"Exported STL for Blender: {output_stl}")
```

### OrcaFlex Results in ParaView

```python
def load_orcaflex_vtk(vtk_dir):
    """Load OrcaFlex VTK export in ParaView."""
    import glob
    vtk_files = sorted(glob.glob(f'{vtk_dir}/*.vtk'))
    if not vtk_files:
        raise FileNotFoundError(f"No VTK files in {vtk_dir}")

    reader = LegacyVTKReader(FileNames=vtk_files)
    reader.UpdatePipeline()
    return reader
```

## Related Skills

- [openfoam](../openfoam/SKILL.md) - OpenFOAM CFD solver interface
- [blender-interface](../../cad/blender/SKILL.md) - 3D rendering and visualization
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Mesh generation

## References

- ParaView Python API: https://kitware.github.io/paraview-docs/latest/python/
- ParaView Catalyst: https://www.paraview.org/in-situ/

---

## Version History

- **1.1.0** (2026-02-24): Validated against VTK 9.6.0 (35/35 checks). Added ParaView 5.11 crash diagnosis for Ubuntu 24.04 + NVIDIA 580. All filter operations, CSV parsing, and data flow verified.
- **1.0.0** (2026-02-23): Initial full interface skill covering pvpython/pvbatch execution, paraview.simple API, filter pipelines, OpenFOAM integration, and validation.
