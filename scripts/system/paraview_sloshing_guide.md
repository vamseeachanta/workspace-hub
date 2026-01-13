# ParaView Visualization Guide - sloshingTank2D Marine Engineering Case

> Specific guide for visualizing the LNG tank sloshing simulation
>
> Case: 2D rectangular tank with prescribed sinusoidal motion
> Results: 800+ time steps from 0 to 40 seconds
> Application: LNG carrier cargo tank sloshing analysis

## Overview

The sloshingTank2D case simulates liquid sloshing in a rectangular tank subjected to sinusoidal motion, representing the dynamics of partially filled LNG cargo tanks during ship motion at sea.

## Quick Start - ParaView Already Launched

ParaView should now be open with the sloshingTank2D VTK files loaded.

### Step 1: Apply Data (if not done automatically)

1. In the **Properties** panel (left side), click the **Apply** button
2. Wait for the data to load

### Step 2: Visualize Water Volume Fraction (alpha.water)

**See where the liquid is:**

1. In the toolbar, find the dropdown that says **"Solid Color"**
2. Change it to **"alpha.water"** (liquid volume fraction)
3. The geometry will now show liquid distribution:
   - **Red/Yellow:** Pure liquid (alpha.water = 1)
   - **Blue/Green:** Mixture zone (free surface)
   - **Dark Blue:** Pure air (alpha.water = 0)

### Step 3: Visualize Pressure Field (p_rgh)

**See impact pressures on tank walls:**

1. Change the color dropdown to **"p_rgh"** (pressure minus hydrostatic)
2. This shows dynamic pressure from sloshing impacts:
   - **Red:** High pressure (impact zones)
   - **Blue:** Low pressure (suction zones)

### Step 4: Create Free Surface Contour

**Visualize the liquid-air interface:**

1. **Top menu:** Filters → Common → **Contour**
2. In Contour properties:
   - **Contour By:** alpha.water
   - **Value:** 0.5 (interface between liquid and air)
3. Click **Apply**
4. This creates a line showing the free surface position
5. Color by velocity magnitude to see wave speed

### Step 5: Animate Through Time

**Watch the sloshing motion:**

1. Click the **Play** button (▶) in the toolbar
2. The simulation will animate through times 0s → 40s
3. Observe:
   - Liquid oscillating back and forth
   - Wave formation on free surface
   - Impact on left and right walls
   - Resonance behavior

### Step 6: Visualize Velocity Field

**See how fast the liquid is moving:**

1. Change color to **"U"** (velocity vector)
2. This shows velocity magnitude
3. Or create a velocity magnitude field:
   - Filters → Alphabetical → **Calculator**
   - Result Array Name: `velocity_magnitude`
   - Expression: `mag(U)`
   - Click **Apply**
   - Color by `velocity_magnitude`

### Step 7: Add Vector Field (Advanced)

**Show velocity direction with arrows:**

1. **Top menu:** Filters → Alphabetical → **Glyph**
2. In Glyph properties:
   - **Glyph Type:** Arrow
   - **Orientation Array:** U
   - **Scale Array:** U
   - **Scale Factor:** 0.1 (adjust for visibility)
3. Click **Apply**
4. This shows velocity direction and magnitude as arrows

## Key Fields in sloshingTank2D

| Field | Description | Units |
|-------|-------------|-------|
| `alpha.water` | Liquid volume fraction | 0-1 (0=air, 1=water) |
| `U` | Velocity vector | m/s |
| `p` | Pressure (absolute) | Pa |
| `p_rgh` | Pressure (minus hydrostatic) | Pa |
| `T` | Temperature | K |

## Understanding the Physics

### Sloshing Mechanism

- **Tank Motion:** Sinusoidal horizontal motion excites liquid
- **Natural Frequency:** Tank dimensions determine natural sloshing frequency
- **Resonance:** When excitation frequency ≈ natural frequency → large amplitudes
- **Impact Loads:** Liquid impacts tank walls creating high pressure spikes

### Expected Observations

1. **Initial Condition (t=0s):**
   - Flat free surface
   - Liquid at rest in lower part of tank

2. **Early Motion (t=1-5s):**
   - Small amplitude waves
   - Liquid starts oscillating

3. **Developed Sloshing (t=10-20s):**
   - Large amplitude oscillations
   - Wave breaking possible
   - High impact pressures on walls

4. **Steady State (t=30-40s):**
   - Regular oscillation pattern
   - Predictable wave behavior
   - Periodic pressure cycles

### Marine Engineering Significance

**LNG Carriers:**
- Transport liquefied natural gas at -162°C
- Partially filled tanks undergo sloshing during ship motion
- Sloshing impacts can:
  - Damage tank insulation
  - Create structural loads
  - Affect ship stability
  - Risk cargo containment failure

**Design Considerations:**
- Tank fill level (typically 10-70% or 95-98% to avoid resonance)
- Baffles to reduce sloshing amplitude
- Membrane insulation must withstand impacts
- Structural strength for impact pressures

## Visualization Recipes

### Recipe 1: Basic Sloshing Animation

```
1. Color by alpha.water
2. Press Play to animate
3. Watch liquid oscillate
Result: See basic sloshing behavior
```

### Recipe 2: Free Surface Tracking

```
1. Add Contour filter: alpha.water = 0.5
2. Color contour by velocity magnitude
3. Animate through time
Result: Track free surface motion and wave speed
```

### Recipe 3: Pressure Analysis

```
1. Color by p_rgh
2. Find time of maximum pressure (scan through animation)
3. Identify impact zones on walls
Result: Locate critical impact areas for structural design
```

### Recipe 4: Velocity Field Analysis

```
1. Create velocity magnitude with Calculator
2. Add Glyph filter with arrows
3. Animate through one oscillation cycle
Result: Understand liquid circulation patterns
```

### Recipe 5: Impact Moment Analysis

```
1. Animate to find maximum impact moment
2. Pause at that time
3. Take screenshot of pressure field
4. Color by p_rgh, rescale to show peak
Result: Document maximum design pressure
```

## Advanced Visualization

### Clip Filter (Cut-Away View)

Since this is a 2D case, clipping may not be necessary, but for 3D variants:

```
1. Filters → Common → Clip
2. Clip Type: Plane
3. Normal: (1, 0, 0) - cut in X direction
4. Origin: (0, 0, 0)
5. Apply
Result: See inside the tank
```

### Time Series Plot

**Track free surface height over time:**

```
1. Tools → Create Custom Filter (advanced)
2. Or export data: File → Save Data → CSV
3. Plot in external tool (Python, Excel)
Result: Frequency analysis of sloshing motion
```

### Comparative View

```
1. Split View Horizontal (button in toolbar)
2. Left view: Color by alpha.water (liquid position)
3. Right view: Color by p_rgh (pressure field)
Result: Correlate liquid motion with pressure
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
- Duration: Covers full 40-second simulation
```

### Export Data

```
File → Save Data
- Format: CSV (for plotting)
- Or VTK (for external analysis)
- Select specific fields to export
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Space** | Play/Pause animation |
| **R** | Reset camera |
| **Left mouse** | Rotate view (3D only) |
| **Shift + Left** | Pan view |
| **Scroll wheel** | Zoom in/out |
| **Ctrl + S** | Save screenshot |
| **Ctrl + Space** | Next time step |
| **Shift + Space** | Previous time step |

## Engineering Analysis Tasks

### Task 1: Determine Natural Frequency

1. Measure sloshing period from animation
2. Calculate frequency: f = 1/T
3. Compare with theoretical natural frequency:
   - For 2D rectangular tank: f = √(g·tanh(kh)·k/2π) / 2π
   - where k = π/L (wavenumber), h = liquid depth, L = tank length

### Task 2: Find Maximum Impact Pressure

1. Scan through animation to find maximum p_rgh
2. Note time and location of impact
3. Document pressure magnitude
4. Use for structural design criteria

### Task 3: Assess Fill Level Effects

**Compare different fill levels (requires running multiple cases):**
- 10% fill - minimal sloshing
- 50% fill - maximum sloshing (near resonance)
- 90% fill - constrained motion

### Task 4: Evaluate Baffle Effectiveness

**For cases with baffles (advanced tutorials):**
- Compare sloshing amplitude with/without baffles
- Measure pressure reduction
- Assess energy dissipation

## Troubleshooting

### Issue: Colors look wrong
- **Solution:** Click "Rescale to Data Range" button (↻) next to color map

### Issue: Can't see liquid
- **Solution:** Make sure coloring by alpha.water, check time step is not at extreme

### Issue: Animation too fast/slow
- **Solution:** Adjust frame rate in animation settings (View → Animation View)

### Issue: Free surface contour looks rough
- **Solution:** Increase mesh resolution or apply smoothing filter

## Case Directory Structure

```
sloshingTank2D/
├── VTK/                           # Visualization files
│   ├── sloshingTank2D_0.vtk       # Time = 0s
│   ├── sloshingTank2D_5.vtk       # Time = 0.05s
│   ├── sloshingTank2D_10.vtk      # Time = 0.10s
│   ...
│   ├── sloshingTank2D_5258.vtk    # Time = 40s (final)
│   └── walls/                     # Wall surface data
├── 0/                             # Initial conditions
├── constant/                      # Physical properties
├── system/                        # Solver settings
│   ├── controlDict               # Simulation control
│   ├── setFieldsDict             # Initial liquid level
│   └── blockMeshDict             # Mesh definition (in resources)
└── Allrun                        # Tutorial workflow script
```

## Simulation Parameters

**Geometry:**
- Tank dimensions: 1m wide × 30m tall (2D extrusion)
- Initial liquid height: Variable (set by setFieldsDict)

**Physics:**
- Solver: incompressibleVoF (two-phase, air-water)
- Time: 0 → 40 seconds
- Time step: 0.01s (adaptive, maxCo = 0.5)
- Output: Every 0.05s (800 files)

**Motion:**
- Prescribed sinusoidal horizontal motion
- Excites sloshing at specific frequency

## Quick Reference Card

**Most Useful Visualizations:**

1. **Liquid position:** Color by alpha.water
2. **Free surface:** Contour at alpha.water = 0.5
3. **Impact pressure:** Color by p_rgh (find maximum)
4. **Liquid velocity:** mag(U) or velocity_magnitude
5. **Animation:** Play to see sloshing cycle
6. **Impact moment:** Pause at max pressure time

**Key Workflow:**

```
Apply → Color by alpha.water → Animate → Find max impact → Pause → Analyze pressure
```

## Related Cases to Explore Next

### Complexity Progression

1. ✅ **sloshingTank2D** - 2D rectangular tank (just completed)
2. **sloshingTank3D** - 3D rectangular tank (~30-60 min)
3. **sloshingTank3D3DoF** - 3D tank with 3 degrees of freedom (~1-2 hours)
4. **sloshingCylinder** - Cylindrical tank (~30-60 min)
5. **sloshingTank3D6DoF** - Full 6-DOF motion (hours)

### Other Marine Cases

- **floatingObject** - Buoyancy and stability (~5 min)
- **floatingObjectWaves** - Offshore platform dynamics (~30 min)
- **damBreak** - Wave impact forces (~2 min)
- **wave** - Wave propagation (~20 min)

## Getting Help

- **ParaView Documentation:** https://www.paraview.org/paraview-docs/
- **OpenFOAM ParaView Guide:** https://doc.cfd.direct/openfoam/user-guide-v13/paraview
- **Marine Engineering Cases:** `openfoam_marine_engineering_cases.md`

---

**Marine Engineering Application Complete! 🚢**

You've successfully run and visualized a practical LNG tank sloshing simulation - a critical analysis for maritime safety and cargo integrity!
