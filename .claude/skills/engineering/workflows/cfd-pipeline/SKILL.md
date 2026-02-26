---
name: cfd-pipeline
description: Cross-program workflow for CFD analysis — geometry (FreeCAD/Gmsh) to meshing (Gmsh/snappyHexMesh) to solving (OpenFOAM) to visualization (ParaView/Blender). Covers data flow, format conversion, and validation between programs.
version: 1.0.1
updated: 2026-02-24
category: workflow
triggers:
- CFD pipeline
- CFD workflow
- geometry to mesh to solve
- OpenFOAM workflow
- end-to-end CFD
- meshing to solving
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires:
- gmsh-meshing
- openfoam
- paraview-interface
see_also:
- freecad-automation
- blender-interface
---
# CFD Pipeline Workflow Skill

End-to-end cross-program workflow for CFD analysis: geometry creation, mesh generation, solver execution, and post-processing visualization.

## Pipeline Overview

```
FreeCAD / External CAD          Gmsh / blockMesh / snappyHexMesh
   (geometry)          ────►        (meshing)
       │                                │
   .step/.stl/.brep                 OpenFOAM polyMesh/
                                        │
                                        ▼
                                   OpenFOAM Solver
                                   (SIMPLE/PIMPLE)
                                        │
                                  time directories/
                                        │
                              ┌─────────┴──────────┐
                              ▼                    ▼
                          ParaView             Blender
                       (analysis viz)      (presentation viz)
```

## Stage 1: Geometry to Mesh

### Path A: FreeCAD/CAD to Gmsh

```bash
# 1. Export from FreeCAD to STEP/BREP
freecadcmd -c "
import FreeCAD, Part
doc = FreeCAD.openDocument('geometry.FCStd')
Part.export(doc.Objects, 'geometry.step')
"

# 2. Mesh with Gmsh
gmsh geometry.step -3 -format msh2 -o mesh.msh \
  -clmin 0.01 -clmax 0.5 \
  -algo del3d
```

### Gmsh to OpenFOAM Conversion

```bash
# Convert Gmsh mesh to OpenFOAM format
gmshToFoam mesh.msh

# Fix boundary patches (Gmsh exports generic names)
# Edit constant/polyMesh/boundary to set correct patch types
```

```python
# Automated Gmsh-to-OpenFOAM boundary patch fix
import re
from pathlib import Path

def fix_boundary_patches(case_dir, patch_map):
    """Fix boundary patch types after gmshToFoam conversion.

    Args:
        case_dir: OpenFOAM case directory
        patch_map: dict of {patch_name: patch_type}
            e.g. {'inlet': 'patch', 'outlet': 'patch', 'walls': 'wall'}
    """
    boundary_file = Path(case_dir) / 'constant' / 'polyMesh' / 'boundary'
    content = boundary_file.read_text()

    for name, ptype in patch_map.items():
        # Replace patch type for named patch
        pattern = rf'({name}\s*\{{[^}}]*type\s+)\w+'
        content = re.sub(pattern, rf'\g<1>{ptype}', content)

    boundary_file.write_text(content)
```

### Path B: CAD to snappyHexMesh (Complex Geometry)

```bash
# 1. Export STL from CAD (FreeCAD or external)
# Ensure STL is watertight and in meters

# 2. Create background mesh with blockMesh
blockMesh

# 3. Run snappyHexMesh
snappyHexMesh -overwrite

# Key files needed:
# - system/blockMeshDict     (background mesh)
# - system/snappyHexMeshDict (refinement + snapping)
# - constant/triSurface/geometry.stl
```

### Validation: Geometry to Mesh

```python
def validate_geometry_to_mesh(stl_path, mesh_dir):
    """Validate the geometry-to-mesh conversion."""
    import subprocess
    checks = {"passed": True, "issues": []}

    # Check STL is readable
    import os
    if not os.path.exists(stl_path):
        checks["issues"].append(f"STL not found: {stl_path}")
        checks["passed"] = False
        return checks

    stl_size = os.path.getsize(stl_path)
    if stl_size < 100:
        checks["issues"].append(f"STL suspiciously small: {stl_size} bytes")
        checks["passed"] = False

    # Check OpenFOAM mesh
    polymesh = os.path.join(mesh_dir, 'constant', 'polyMesh', 'points')
    if not os.path.exists(polymesh):
        checks["issues"].append("No polyMesh/points — mesh conversion failed")
        checks["passed"] = False
        return checks

    # Run checkMesh
    result = subprocess.run(
        ['checkMesh', '-case', mesh_dir],
        capture_output=True, text=True
    )
    if 'FAILED' in result.stdout:
        checks["issues"].append("checkMesh reports failures")
        checks["passed"] = False

    # Extract mesh stats
    import re
    cells_match = re.search(r'cells:\s+(\d+)', result.stdout)
    if cells_match:
        checks["cells"] = int(cells_match.group(1))

    return checks
```

## Stage 2: Mesh to Solver

### OpenFOAM Case Setup from Mesh

```bash
# After meshing, set up the solver case:
# 1. Copy 0/ boundary conditions (must match mesh patches)
# 2. Configure system/controlDict
# 3. Configure system/fvSchemes and system/fvSolution
# 4. Set physical properties in constant/

# Check that boundary names in 0/ match polyMesh/boundary
grep -r "type" constant/polyMesh/boundary | grep -v "//"
ls 0/  # Should have U, p, k, omega, etc.
```

### Boundary Condition Consistency Check

```python
def check_bc_consistency(case_dir):
    """Verify boundary conditions match mesh patches."""
    from pathlib import Path
    import re

    # Get mesh patches
    boundary_file = Path(case_dir) / 'constant' / 'polyMesh' / 'boundary'
    boundary_text = boundary_file.read_text()
    mesh_patches = set(re.findall(r'^\s+(\w+)\s*$', boundary_text, re.MULTILINE))

    # Get BC patches from 0/ files
    zero_dir = Path(case_dir) / '0'
    issues = []

    for bc_file in zero_dir.glob('*'):
        if bc_file.is_file():
            content = bc_file.read_text()
            bc_patches = set(re.findall(r'^\s+(\w+)\s*\{', content, re.MULTILINE))

            # Remove non-patch entries
            bc_patches -= {'boundaryField', 'internalField', 'FoamFile', 'dimensions'}

            missing = bc_patches - mesh_patches
            if missing:
                issues.append(f"{bc_file.name}: references non-existent patches: {missing}")

    return issues
```

### Solver Execution

```bash
# Serial execution
simpleFoam -case /path/to/case 2>&1 | tee log.simpleFoam

# Parallel execution
decomposePar -case /path/to/case
mpirun -np 4 simpleFoam -parallel -case /path/to/case 2>&1 | tee log.simpleFoam
reconstructPar -case /path/to/case
```

## Stage 3: Solver to Visualization

### OpenFOAM to ParaView

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

### OpenFOAM to Blender (Presentation Rendering)

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

## Stage 4: Error Propagation and Where to Validate

### Validation Points in the Pipeline

| Stage | What to Check | Tool | Failure Mode |
|-------|--------------|------|--------------|
| **Geometry** | Watertight STL, units (meters) | FreeCAD / meshio | Open surfaces break meshing |
| **Mesh** | checkMesh quality, patch names | OpenFOAM checkMesh | Bad cells cause solver divergence |
| **BCs** | Patches match mesh, physically consistent | Script above | Missing BC crashes solver |
| **Solver** | Residuals converging, Courant < 1 | Log parsing | Divergence = wrong mesh/BCs/schemes |
| **Results** | Value ranges physical, conservation | ParaView validation | Non-physical = wrong setup |
| **Export** | Image non-blank, data non-empty | File size check | Rendering/export config |

### Full Pipeline Validation Script

```python
def validate_cfd_pipeline(case_dir, output_dir):
    """Validate entire CFD pipeline from mesh to results."""
    import subprocess
    import os

    status = {"stages": {}, "overall": True}

    # 1. Mesh quality
    mesh_check = subprocess.run(
        ['checkMesh', '-case', case_dir],
        capture_output=True, text=True
    )
    mesh_ok = 'FAILED' not in mesh_check.stdout
    status["stages"]["mesh"] = {"passed": mesh_ok}
    if not mesh_ok:
        status["overall"] = False

    # 2. Solver completion
    import glob
    time_dirs = [d for d in glob.glob(os.path.join(case_dir, '[0-9]*'))
                 if os.path.isdir(d) and d.split('/')[-1] != '0']
    solver_ok = len(time_dirs) > 0
    status["stages"]["solver"] = {"passed": solver_ok, "time_steps": len(time_dirs)}
    if not solver_ok:
        status["overall"] = False

    # 3. Results physical
    # Check residuals from log
    log_files = glob.glob(os.path.join(case_dir, 'log.*'))
    if log_files:
        import re
        log_text = open(log_files[0]).read()
        final_residuals = re.findall(r'Solving for (\w+).*Final residual = ([\d.e+-]+)', log_text)
        if final_residuals:
            last_residuals = {}
            for name, val in final_residuals:
                last_residuals[name] = float(val)
            converged = all(v < 1e-3 for v in last_residuals.values())
            status["stages"]["convergence"] = {"passed": converged, "residuals": last_residuals}
            if not converged:
                status["overall"] = False

    # 4. Visualization output
    if os.path.isdir(output_dir):
        images = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        viz_ok = len(images) > 0 and all(
            os.path.getsize(os.path.join(output_dir, f)) > 1000 for f in images
        )
        status["stages"]["visualization"] = {"passed": viz_ok, "images": len(images)}

    return status
```

## Quick Reference: File Flow

```
FreeCAD (.FCStd) ──export──► .step/.stl
                                  │
            gmsh (.geo) ──mesh──► .msh ──gmshToFoam──► polyMesh/
                                                           │
            blockMesh ──────────────────────────────► polyMesh/
                                                           │
                                  snappyHexMesh ───────► polyMesh/
                                                           │
                              OpenFOAM solver ──────► time dirs (0.1/, 0.2/, ...)
                                                           │
                              foamToVTK ────────────► VTK/*.vtk
                                                           │
                    ┌──────────────────────────────────────┤
                    ▼                                      ▼
              ParaView (.foam)                    Blender (.stl via meshio)
              ├── screenshots                     ├── high-quality renders
              ├── CSV line probes                 └── animation
              └── animations
```

## Related Skills

- [openfoam](../../cfd/openfoam/SKILL.md) - OpenFOAM solver interface
- [paraview-interface](../../cfd/paraview/SKILL.md) - ParaView visualization
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Mesh generation
- [freecad-automation](../../cad/freecad-automation/SKILL.md) - CAD geometry
- [blender-interface](../../cad/blender/SKILL.md) - 3D rendering

---

## Version History

- **1.0.1** (2026-02-24): Fixed pvbatch -c inline flag (not supported) → script file pattern (validated 148/151→151/151)
- **1.0.0** (2026-02-23): Initial cross-program workflow skill for CFD pipeline (WRK-372 Phase 4).
