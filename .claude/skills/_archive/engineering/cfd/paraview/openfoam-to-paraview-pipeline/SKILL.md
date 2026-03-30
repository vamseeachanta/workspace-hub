---
name: paraview-interface-openfoam-to-paraview-pipeline
description: 'Sub-skill of paraview-interface: OpenFOAM to ParaView Pipeline (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# OpenFOAM to ParaView Pipeline (+2)

## OpenFOAM to ParaView Pipeline


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


## VTK Export for Blender


```python
def export_surface_for_blender(source, output_stl):
    """Export surface mesh as STL for Blender import."""
    surface = ExtractSurface(Input=source)
    triangulate = Triangulate(Input=surface)
    SaveData(output_stl, proxy=triangulate)
    print(f"Exported STL for Blender: {output_stl}")
```


## OrcaFlex Results in ParaView


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
