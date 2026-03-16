---
name: cfd-pipeline-openfoam-to-paraview
description: 'Sub-skill of cfd-pipeline: OpenFOAM to ParaView (+1).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# OpenFOAM to ParaView (+1)

## OpenFOAM to ParaView


```bash
# Create .foam trigger file for ParaView
touch /path/to/case/case.foam

# Launch ParaView visualization
pvbatch visualize.py
```

```python
# visualize.py — Automated ParaView post-processing
from paraview.simple import *

def openfoam_post_process(case_dir, output_dir):
    """Generate standard CFD visualization outputs."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Load OpenFOAM case
    foam_file = os.path.join(case_dir, 'case.foam')
    if not os.path.exists(foam_file):
        open(foam_file, 'w').close()

    reader = OpenFOAMReader(FileName=foam_file)
    reader.MeshRegions = ['internalMesh']
    reader.CellArrays = ['U', 'p']

    # Last time step
    anim = GetAnimationScene()
    anim.UpdateAnimationUsingDataTimeSteps()
    anim.AnimationTime = reader.TimestepValues[-1]

    view = GetActiveViewOrCreate('RenderView')
    view.ViewSize = [1920, 1080]

    # Velocity magnitude slice
    calc = Calculator(Input=reader)
    calc.Function = 'mag(U)'
    calc.ResultArrayName = 'Umag'

    slice_z = Slice(Input=calc)
    slice_z.SliceType.Normal = [0, 0, 1]

    display = Show(slice_z, view)
    ColorBy(display, ('POINTS', 'Umag'))
    display.SetScalarBarVisibility(view, True)
    view.ResetCamera()
    Render()
    SaveScreenshot(os.path.join(output_dir, 'velocity_slice.png'), view)

    # Pressure iso-surface
    Hide(slice_z, view)
    contour = Contour(Input=reader)
    contour.ContourBy = ['POINTS', 'p']
    contour.Isosurfaces = [0]
    display2 = Show(contour, view)
    Render()
    SaveScreenshot(os.path.join(output_dir, 'pressure_iso.png'), view)

    # Export line probe data (e.g., centerline)
    probe = PlotOverLine(Input=reader)
    probe.Point1 = [0, 0, 0]
    probe.Point2 = [1, 0, 0]
    probe.Resolution = 200
    SaveData(os.path.join(output_dir, 'centerline_data.csv'), proxy=probe)
```


## OpenFOAM to Blender (Presentation Rendering)


```bash
# 1. Export from OpenFOAM to VTK
foamToVTK -case /path/to/case -latestTime

# 2. Convert VTK to STL via ParaView script (pvbatch does not support -c flag)
cat > vtk_to_stl.py << 'PYEOF'
from paraview.simple import *
r = LegacyVTKReader(FileNames=['VTK/case_1000.vtk'])
s = ExtractSurface(Input=r)
t = Triangulate(Input=s)
SaveData('surface.stl', proxy=t)
PYEOF
pvbatch vtk_to_stl.py

# 3. Import into Blender
blender --background --python render_cfd.py -- --input surface.stl --output render.png
```
