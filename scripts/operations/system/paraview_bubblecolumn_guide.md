# ParaView Visualization Guide - bubbleColumn Multiphase Case

> Specific guide for visualizing the air-water bubble column simulation
>
> Case: Multiphase Eulerian (air + water)
> Results: Parallel simulation (8 cores, reconstructed)

## Overview

The bubbleColumn case simulates air bubbles rising through water in a vertical column. This is a multiphase Eulerian simulation where both phases (air and water) are treated as interpenetrating continua.

## Quick Start - ParaView Already Launched

ParaView should now be open with the bubbleColumn VTK file loaded.

### Step 1: Apply Data (if not done automatically)

1. In the **Properties** panel (left side), click the **Apply** button
2. Wait for the data to load

### Step 2: Visualize Air Volume Fraction

**See where the air bubbles are:**

1. In the toolbar, find the dropdown that says **"Solid Color"**
2. Change it to **"alpha.air"** (air volume fraction)
3. The geometry will now show air distribution:
   - **Red/Yellow:** High air concentration (bubbles)
   - **Blue/Purple:** Low air concentration (mostly water)

### Step 3: Visualize Water Volume Fraction

**See the water distribution:**

1. Change the color dropdown to **"alpha.water"**
2. This shows the complementary view:
   - **Red/Yellow:** High water concentration
   - **Blue/Purple:** Low water concentration (where air is)

### Step 4: Visualize Velocity Fields

**Air velocity (bubble motion):**

1. Change color to **"U.air"** (air velocity vector)
2. This shows how fast the air bubbles are moving

**Water velocity:**

1. Change color to **"U.water"** (water velocity)
2. This shows the water circulation induced by rising bubbles

### Step 5: Create Velocity Magnitude

**Calculate speed from velocity vectors:**

1. **Top menu:** Filters → Alphabetical → **Calculator**
2. In Calculator properties:
   - **Result Array Name:** `air_speed`
   - **Expression:** `mag(U.air)`
3. Click **Apply**
4. Change color dropdown to `air_speed`
5. Repeat for water: `mag(U.water)` → `water_speed`

### Step 6: Visualize Temperature

**Air temperature:**

1. Change color to **"T.air"**
2. Shows temperature distribution in air phase

**Water temperature:**

1. Change color to **"T.water"**
2. Shows temperature in water phase

### Step 7: Visualize Pressure

1. Change color to **"p_rgh"** (pressure)
2. Shows pressure field accounting for gravity
3. Or use **"p"** for absolute pressure

### Step 8: Create Isosurfaces (Bubble Surfaces)

**Visualize bubble boundaries:**

1. **Top menu:** Filters → Common → **Contour**
2. In Contour properties:
   - **Contour By:** alpha.air
   - **Value:** 0.5 (interface between air and water)
3. Click **Apply**
4. This creates surfaces where air fraction = 50%
5. Color by velocity to see bubble rise speed

### Step 9: Add Streamlines (Flow Patterns)

**Show flow patterns in water:**

1. Make sure you have **bubbleColumn** selected (not Contour)
2. **Top menu:** Filters → Alphabetical → **Stream Tracer**
3. In Stream Tracer properties:
   - **Vectors:** U.water
   - **Seed Type:** Point Cloud
   - **Center:** (0, 0, 0.15) - middle height
   - **Radius:** 0.03
   - **Number of Points:** 50
4. Click **Apply**
5. Color by `water_speed` to see flow velocity

### Step 10: Create Volume Rendering (Advanced)

**3D volume view of air bubbles:**

1. Select **bubbleColumn** object
2. Change representation from **Surface** to **Volume**
3. Adjust **Opacity** in color map editor
4. Color by **alpha.air** for bubble visualization

### Step 11: Animate Through Time

**Watch bubble evolution:**

1. Click the **Play** button (▶) in the toolbar
2. The simulation will animate through times 1s → 5s
3. Adjust animation speed with time controls
4. You can see bubbles rising and coalescing

## Key Fields in bubbleColumn

| Field | Description | Units |
|-------|-------------|-------|
| `alpha.air` | Air volume fraction | 0-1 (0=no air, 1=pure air) |
| `alpha.water` | Water volume fraction | 0-1 (0=no water, 1=pure water) |
| `U.air` | Air velocity vector | m/s |
| `U.water` | Water velocity vector | m/s |
| `p` | Pressure | Pa |
| `p_rgh` | Pressure (minus hydrostatic) | Pa |
| `T.air` | Air temperature | K |
| `T.water` | Water temperature | K |
| `k.air` | Air turbulent kinetic energy | m²/s² |
| `k.water` | Water turbulent kinetic energy | m²/s² |
| `epsilon.air` | Air turbulence dissipation | m²/s³ |
| `epsilon.water` | Water turbulence dissipation | m²/s³ |

## Visualization Recipes

### Recipe 1: Bubble Visualization

```
1. Color by alpha.air
2. Add Contour filter: alpha.air = 0.5
3. Color contour by mag(U.air)
4. Animate through time
Result: See individual bubbles colored by rise speed
```

### Recipe 2: Flow Patterns

```
1. Add Stream Tracer with U.water vectors
2. Color streamlines by water_speed
3. Add Glyph filter (arrows) to show flow direction
Result: Understand water circulation patterns
```

### Recipe 3: Temperature Distribution

```
1. Create slice at z=0.15 (middle height)
2. Color by T.water
3. Add contour lines for temperature levels
Result: See temperature gradients in column
```

### Recipe 4: Pressure Field

```
1. Color by p_rgh
2. Create vertical slice (y=0 plane)
3. Add warp filter to extrude by pressure
Result: 3D pressure visualization
```

### Recipe 5: Turbulence Intensity

```
1. Use Calculator: sqrt(k.water) for turbulence intensity
2. Color by result
3. Add streamlines colored by turbulence
Result: See high turbulence regions (near bubbles)
```

## Understanding the Physics

### Bubble Rise Mechanism

- **Buoyancy:** Air is less dense than water → bubbles rise
- **Drag:** Water resistance slows bubble rise
- **Coalescence:** Small bubbles merge into larger ones
- **Wake:** Rising bubbles create water circulation behind them

### Expected Observations

1. **Inlet (bottom):** Small bubbles enter with uniform size
2. **Middle region:** Bubbles coalesce, grow larger
3. **Outlet (top):** Larger bubbles exit, faster rise velocity
4. **Water flow:** Downward near walls, upward in center (induced by bubbles)

### Volume Fractions

- **alpha.air + alpha.water = 1.0** everywhere (conservation)
- **High alpha.air (>0.8):** Inside bubbles
- **Low alpha.air (<0.2):** Bulk water with dispersed tiny bubbles
- **alpha.air ≈ 0.5:** Bubble surface/interface

## Advanced Visualization

### Clip Filter (Cut-Away View)

```
1. Filters → Common → Clip
2. Clip Type: Plane
3. Normal: (1, 0, 0) - cut in X direction
4. Origin: (0, 0, 0)
5. Apply
Result: See inside the column
```

### Multiple Views

```
1. Split View Horizontal (button in toolbar)
2. Left view: alpha.air (bubble distribution)
3. Right view: U.water streamlines (water flow)
Result: Compare phases side-by-side
```

### Time Comparison

```
1. File → Open → Load multiple time steps
2. Filters → Temporal → Temporal Interpolator
3. Create snapshots at different times
Result: Before/after comparison
```

## Exporting Results

### Save Images

```
File → Save Screenshot
- Resolution: 1920x1080 (or higher)
- Transparent background: optional
- Format: PNG (best quality)
```

### Save Animation

```
File → Save Animation
- Format: AVI or MP4
- Frame rate: 30 fps
- Duration: 5 seconds (matches simulation)
```

### Export Data

```
File → Save Data
- Format: CSV (for plotting)
- Or VTK (for external analysis)
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Space** | Play/Pause animation |
| **R** | Reset camera |
| **Left mouse** | Rotate view |
| **Shift + Left** | Pan view |
| **Scroll wheel** | Zoom in/out |
| **Ctrl + S** | Save screenshot |
| **Ctrl + Space** | Next time step |

## Troubleshooting

### Issue: Colors look wrong
- **Solution:** Click "Rescale to Data Range" button (↻) next to color map

### Issue: Can't see bubbles
- **Solution:** Make sure coloring by alpha.air, check time step has bubbles

### Issue: Streamlines disappear
- **Solution:** Adjust seed point location, increase number of seeds

### Issue: Slow performance
- **Solution:** Reduce number of points, use lower resolution, or skip time steps

## Time Step Information

The bubbleColumn case has these time steps:

- **Time 1s:** bubbleColumn_67.vtk - Early stage
- **Time 2s:** bubbleColumn_136.vtk - Bubble formation
- **Time 3s:** bubbleColumn_231.vtk - Coalescence begins
- **Time 4s:** bubbleColumn_359.vtk - Larger bubbles
- **Time 5s:** bubbleColumn_510.vtk - Fully developed flow

Load different time steps to see evolution:
```
File → Open → bubbleColumn/VTK/bubbleColumn_510.vtk (final state)
```

## ParaView Performance Tips

1. **Reduce data:** Use Extract Subset filter for large datasets
2. **Turn off automatic updates:** Uncheck "Auto Apply" in properties
3. **Use LOD:** Adjust Level of Detail in View Settings
4. **Close unused filters:** Delete intermediate filter results
5. **GPU rendering:** Ensure GPU acceleration is enabled (Edit → Settings)

## Saving Your ParaView State

To save your visualization setup:

```
File → Save State
- Saves: All filters, coloring, camera position
- Later: File → Load State to restore
```

## Case Directory Structure

```
bubbleColumn/
├── VTK/                          # Visualization files
│   ├── bubbleColumn_67.vtk      # Time = 1s
│   ├── bubbleColumn_136.vtk     # Time = 2s
│   ├── bubbleColumn_231.vtk     # Time = 3s
│   ├── bubbleColumn_359.vtk     # Time = 4s
│   ├── bubbleColumn_510.vtk     # Time = 5s (final)
│   ├── inlet/                   # Inlet patch data
│   ├── outlet/                  # Outlet patch data
│   └── walls/                   # Wall patch data
├── 1/ 2/ 3/ 4/ 5/               # Reconstructed time directories
├── constant/                     # Physical properties
├── system/                       # Solver settings
└── log.foamRun.parallel         # Parallel simulation log
```

## Quick Reference Card

**Most Useful Visualizations:**

1. **Air bubbles:** Color by alpha.air
2. **Bubble surfaces:** Contour at alpha.air = 0.5
3. **Bubble speed:** mag(U.air)
4. **Water flow:** Stream Tracer with U.water
5. **Pressure:** Color by p_rgh
6. **Temperature:** Color by T.water
7. **Animation:** Play button to see time evolution

**Key Workflow:**

```
Apply → Color by alpha.air → Add Contour → Color by velocity → Animate
```

## Getting Help

- **ParaView Documentation:** https://www.paraview.org/paraview-docs/
- **OpenFOAM ParaView Guide:** https://doc.cfd.direct/openfoam/user-guide-v13/paraview
- **Multiphase Tutorial:** In OpenFOAM v13 tutorials folder

---

**Enjoy exploring your multiphase simulation results! 🫧**
