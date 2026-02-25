# OpenFOAM Tutorial Run Notes

> Status: Research completed 2026-02-24
> Machine: ace-linux-2 (OpenFOAM ESI v2312, verified installed)
> WRK: WRK-343 (feeds WRK-047, WRK-292)

## Summary

OpenFOAM ESI v2312 is confirmed installed and operational on ace-linux-2. The pitzDaily
tutorial was run as part of WRK-290 installation verification, confirming end-to-end
solver execution (converged in 281 iterations). This document collects the tutorial
evidence from WRK-290 and adds pattern documentation for the remaining tutorials that
must be run when parallelism permits.

## Installation State (ace-linux-2 as of 2026-02-24)

| Component | Version | Status |
|-----------|---------|--------|
| OpenFOAM | ESI v2312 | Installed via apt (openfoam.org repo) |
| blockMesh | bundled with v2312 | Verified working |
| simpleFoam | bundled with v2312 | Verified — ran pitzDaily (281 iter) |
| interFoam | bundled with v2312 | Available (not yet run) |
| snappyHexMesh | bundled with v2312 | Available (not yet run) |
| paraFoam/ParaView | 5.11.2 | Installed via apt; pvpython verified |
| foamToVTK | bundled with v2312 | Available for headless post-processing |

Source environment: `/opt/openfoam2312/etc/bashrc`
Tutorial root: `/opt/openfoam2312/tutorials/`

## Tutorial 1: pitzDaily (simpleFoam, k-epsilon turbulence)

**Status: COMPLETED** (run as WRK-290 acceptance test, 2026-02-21)

### What this tutorial tests
- incompressible steady-state RANS solver (simpleFoam)
- k-epsilon turbulence model (standard)
- blockMesh hex mesh generation
- Convergence in ~200-300 iterations typical

### Commands
```bash
source /opt/openfoam2312/etc/bashrc
cp -r /opt/openfoam2312/tutorials/incompressible/simpleFoam/pitzDaily ~/foam/run/
cd ~/foam/run/pitzDaily
blockMesh
simpleFoam 2>&1 | tee log.simpleFoam
```

### Result (WRK-290 log)
- blockMesh: completed, generated ~2700 hex cells
- simpleFoam: converged in **281 iterations**
- Final Ux residual: < 1e-4 (target met)
- Final p residual: < 1e-4 (target met)
- k, epsilon residuals: < 1e-4

### Key files observed
```
pitzDaily/
├── 0/
│   ├── U              # Initial/BC velocity field
│   ├── p              # Pressure
│   ├── k              # Turbulent kinetic energy
│   └── epsilon        # Dissipation rate
├── constant/
│   ├── transportProperties   # nu = 1e-5 m2/s (air-ish)
│   └── turbulenceProperties  # RAS, kEpsilon model
└── system/
    ├── blockMeshDict    # 2D channel, inlet/outlet/top/bottom/frontBack
    ├── controlDict      # endTime 2000, writeInterval 100
    ├── fvSchemes        # Gauss linear/limitedLinear, standard schemes
    └── fvSolution       # SIMPLE algorithm, relaxation factors
```

### Notes for WRK-047
- blockMeshDict uses `vertices`, `blocks`, `edges`, `boundary` sections
- Boundary patches: inlet (fixedValue), outlet (zeroGradient), walls (noSlip)
- controlDict: `application simpleFoam; endTime 2000; deltaT 1; writeInterval 100`
- fvSchemes: div(phi,U) uses `Gauss linearUpwind grad(U)` — common for RANS

---

## Tutorial 2: cavity (icoFoam — laminar, transient)

**Status: PENDING** (scheduled for next ace-linux-2 session)

### What this tutorial tests
- laminar transient incompressible solver (icoFoam)
- blockMesh lid-driven cavity
- Time-stepping, PISO algorithm
- paraFoam post-processing workflow

### Planned commands
```bash
source /opt/openfoam2312/etc/bashrc
cp -r /opt/openfoam2312/tutorials/incompressible/icoFoam/cavity/cavity ~/foam/run/
cd ~/foam/run/cavity
blockMesh
icoFoam 2>&1 | tee log.icoFoam
paraFoam &   # or foamToVTK for headless
```

### Expected outcome
- blockMesh generates ~400 hex cells (20x20 default mesh)
- icoFoam runs to endTime=0.5 (500 steps at deltaT=0.001)
- Lid velocity U=(1,0,0), walls no-slip, Re≈100
- Classic vortex pattern visible in post-processing

### Files of interest
- `blockMeshDict`: 2D square cavity, simple `hex` block with `simpleGrading`
- `controlDict`: `application icoFoam; endTime 0.5; deltaT 0.001`
- `transportProperties`: `nu 0.01` (kinematic viscosity)
- No turbulenceProperties (laminar)

### Expected runtime
- < 30 seconds on ace-linux-2

---

## Tutorial 3: damBreak (interFoam — VOF multiphase)

**Status: PENDING** (scheduled for next ace-linux-2 session)

### What this tutorial tests
- Volume-of-fluid (VOF) free surface solver (interFoam)
- Two-phase flow (water + air)
- setFields for initial phase distribution
- Dynamic time-stepping (Courant number control)

### Planned commands
```bash
source /opt/openfoam2312/etc/bashrc
cp -r /opt/openfoam2312/tutorials/multiphase/interFoam/laminar/damBreak ~/foam/run/
cd ~/foam/run/damBreak
blockMesh
setFields         # Initialize water column in bottom-left
interFoam 2>&1 | tee log.interFoam
foamToVTK         # For headless post-processing
```

### Expected outcome
- 2D dam break simulation
- Water column collapses, propagates along floor
- alpha.water field: 0=air, 1=water, intermediate=interface

### Files of interest
- `constant/transportProperties`: two phases — water (rho=1000, nu=1e-6) and air (rho=1, nu=1.48e-5)
- `constant/turbulenceProperties`: laminar (no turbulence model)
- `system/setFieldsDict`: initial water column region definition
- `0/alpha.water`: initial phase fraction
- `controlDict`: `maxCo 0.5` (Courant number limit)

### Notes for WRK-047
- transportProperties in interFoam uses `phases (water air)` block syntax — different from simpleFoam
- `setFields` utility is essential for VOF initialization
- alpha.water initial condition uses `boxToCell` or `zoneToCell` selectors

### Expected runtime
- 2-5 minutes on ace-linux-2

---

## Tutorial 4: motorBike (simpleFoam + snappyHexMesh — external aero)

**Status: PENDING** (requires more disk space — ~2GB)

### What this tutorial tests
- Complex surface meshing via snappyHexMesh
- STL geometry import workflow
- External aerodynamics boundary conditions
- Wake refinement and boundary layers

### Planned commands
```bash
source /opt/openfoam2312/etc/bashrc
cp -r /opt/openfoam2312/tutorials/incompressible/simpleFoam/motorBike ~/foam/run/
cd ~/foam/run/motorBike
./Allrun   # uses: blockMesh → decomposePar → snappyHexMesh (parallel) → simpleFoam
```

### Expected outcome
- snappyHexMesh generates ~6M cells from motorbike STL
- simpleFoam runs for ~500 iterations
- Force coefficients on motorbike surface extracted

### Files of interest
- `system/snappyHexMeshDict`: geometry block (STL file ref), castellatedMesh, snap, addLayers
- `constant/triSurface/motorBike.obj.gz`: STL/OBJ geometry
- `system/decomposeParDict`: scotch decomposition for parallel meshing
- `Allrun` / `Allclean`: reference scripts for automation pattern

### Notes for WRK-047
- snappyHexMeshDict geometry section uses `type triSurfaceMesh; file "motorBike.obj"`
- `castellatedMeshControls`: `maxLocalCells`, `maxGlobalCells`, `refinementSurfaces`, `refinementRegions`
- `snapControls`: `nSmoothPatch`, `tolerance`, `nSolveIter`, `nRelaxIter`
- `addLayersControls`: `relativeSizes true`, `layers { motorBike { nSurfaceLayers 3; } }`
- This is the primary template for hull meshing in WRK-047

### Expected runtime
- blockMesh: ~30 seconds
- snappyHexMesh (parallel, 4 cores): ~10-20 minutes
- simpleFoam (500 iter): ~30-60 minutes

---

## Automation Pattern: Allrun / Allclean

All complex OpenFOAM tutorial cases include `Allrun` and `Allclean` shell scripts.
These are the canonical patterns for case automation and should be replicated in WRK-047.

### Allrun pattern (from motorBike)
```bash
#!/bin/sh
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Source run functions

runApplication blockMesh
runApplication $(getApplication)                    # reads controlDict application
```

### More complex Allrun (parallel + snappy)
```bash
#!/bin/sh
cd "${0%/*}" || exit
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions

runApplication blockMesh
runApplication decomposePar -copyZero
runParallel snappyHexMesh -overwrite
runApplication reconstructParMesh -constant
runParallel $(getApplication)
runApplication reconstructPar
```

### Key RunFunctions
- `runApplication <cmd>`: runs cmd, logs to `log.<cmd>`; exits on failure
- `runParallel <cmd>`: runs `mpirun -np <NP> <cmd> -parallel`
- `getApplication`: reads `application` field from `system/controlDict`

### WRK-047 implication
The `runner.py` in Phase 5 should replicate this pattern:
- subprocess.run for each step with logging to `log.<solver>` files
- Check return codes and parse residuals from log files
- Support sequential and parallel execution paths

---

## Post-Processing Notes

### paraFoam (GUI)
- Launches ParaView with OpenFOAM reader plugin
- Requires X display (use `paraFoam -builtin` for built-in reader)
- Not suitable for headless ace-linux-2 automation

### foamToVTK (headless)
```bash
foamToVTK -latestTime    # Convert most recent time step
foamToVTK -time '100:500' # Convert time range
```
- Produces `VTK/` directory with `.vtp` and `.vtu` files
- Readable by pyvista and ParaView

### pvpython (headless scripting)
```bash
pvpython --force-offscreen-rendering script.py
```
- ParaView Python API for automated post-processing
- Verified working on ace-linux-2 (WRK-290)

### postProcess utility
```bash
postProcess -func forceCoeffs -latestTime
postProcess -func probes
```
- Runs function objects defined in controlDict or specified on command line
- Most useful for automated force/moment extraction

---

## Known Issues

| Issue | Impact | Resolution |
|-------|--------|------------|
| paraFoam requires X display | Cannot use GUI on ace-linux-2 headlessly | Use foamToVTK + pvpython, or paraFoam -builtin |
| motorBike needs ~2GB disk | May not fit in current workspace | Use smaller mesh config or confirm disk available |
| Parallel runs require mpirun | snappyHexMesh parallel needs `decomposePar` first | Follow Allrun script pattern |

---

*Generated: 2026-02-24 | WRK-343*
