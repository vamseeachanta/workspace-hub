# ParaView Visualization Guide for OpenFOAM v13

## Quick Start

### Step 1: Launch ParaView from OpenFOAM Case

```bash
cd ~/openfoam-test/pitzDaily
of13  # Load OpenFOAM environment
paraFoam  # Launch ParaView with OpenFOAM reader
```

### Step 2: Load the Data in ParaView

1. **ParaView will open** with an OpenFOAM reader dialog
2. **Click "Apply"** in the Properties panel (left side)
3. Wait for data to load

### Step 3: Visualize Velocity

1. In the **toolbar**, find the dropdown that says "Solid Color"
2. Change it to **"U"** (velocity vector field)
3. The geometry will now show velocity colors

### Step 4: Create Velocity Magnitude View

1. **Top menu**: Filters → Alphabetical → Calculator
2. In the Calculator properties:
   - Result Array Name: `velocity_magnitude`
   - Expression: `mag(U)`
3. Click **Apply**
4. Change the color dropdown to `velocity_magnitude`

### Step 5: Add Streamlines

1. **Top menu**: Filters → Alphabetical → Stream Tracer
2. In Stream Tracer properties:
   - Seed Type: Point Cloud
   - Center: adjust to (0, 0, 0)
   - Radius: 0.025
   - Number of Points: 50
3. Click **Apply**
4. Color streamlines by `U` or `velocity_magnitude`

### Step 6: Create Cross-Section Slice

1. **Top menu**: Filters → Common → Slice
2. In Slice properties:
   - Origin: (0.1, 0, 0) - middle of domain
   - Normal: (1, 0, 0) - perpendicular to flow
3. Click **Apply**
4. Color by `p` (pressure) or `U`

### Step 7: Animate Through Time

1. Click the **Play** button (▶) in the toolbar
2. The simulation will animate from t=0 to t=0.3s
3. Adjust speed with the time controls

## Advanced Visualizations

### Pressure Contours

1. Load data and apply
2. Color by: `p` (pressure)
3. Filters → Common → Contour
   - Contour By: `p`
   - Value Range: adjust based on data

### Turbulence Visualization

1. Color by: `k` (turbulent kinetic energy)
2. Or by: `epsilon` (turbulence dissipation rate)

### Wall Shear Stress

1. Filters → Alphabetical → Generate Surface Normals
2. Apply
3. Filters → Alphabetical → Calculator
   - Expression: `mag(wallShearStress)`

## Quick Tips

### Camera Controls
- **Rotate**: Left mouse drag
- **Pan**: Middle mouse drag or Shift + Left mouse
- **Zoom**: Scroll wheel or Right mouse drag

### Color Scale
- Click on the color bar to edit ranges
- Use "Rescale to Data Range" for automatic adjustment

### Save Images
- File → Save Screenshot
- Adjust resolution (e.g., 1920x1080)

### Save Animation
- File → Save Animation
- Choose format (AVI, MP4, etc.)

## Alternative: Using VTK Files

If paraFoam doesn't work, use the VTK files:

```bash
cd ~/openfoam-test/pitzDaily
# VTK files are in VTK/ directory
# Open ParaView separately and load:
# File → Open → ~/openfoam-test/pitzDaily/VTK/pitzDaily_1225.vtk
```

## Troubleshooting

### "Could not find OpenFOAM reader"
- Make sure you launched with `paraFoam` command
- Or manually load VTK files instead

### "No data appears"
- Click "Apply" in the Properties panel
- Check that case has time directories

### Display issues
- Try: Edit → Settings → Render View → Use Offscreen Rendering

## Results in This Case

**Location**: `~/openfoam-test/pitzDaily/`

**Files generated**:
- VTK files in `VTK/` directory
- Time directories: `0.01` through `0.3`
- Velocity magnitude field in `0.3/mag(U)`

**Expected visualizations**:
- Flow separation at the step
- Recirculation zone after expansion
- Velocity gradients near walls
- Pressure drop across domain

## Documentation

- OpenFOAM v13 ParaView Guide: https://doc.cfd.direct/openfoam/user-guide-v13/paraview
- ParaView User Guide: https://www.paraview.org/paraview-guide/
