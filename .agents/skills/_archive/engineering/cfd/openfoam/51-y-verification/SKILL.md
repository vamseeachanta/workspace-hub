---
name: openfoam-51-y-verification
description: 'Sub-skill of openfoam: 5.1 y+ Verification (+5).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 5.1 y+ Verification (+5)

## 5.1 y+ Verification


```bash
# Compute y+ post-hoc
simpleFoam -postProcess -func yPlus -latestTime
```

Or add to controlDict:
```cpp
functions { #includeFunc yPlus }
```

**Target y+ ranges:**

| Approach | y+ target | When to use |
|----------|-----------|-------------|
| Wall-resolved (low-Re) | < 1 | Accurate wall heat transfer, separation |
| Wall functions (high-Re) | 30-300 | Industrial flows, coarser meshes |
| Buffer layer (avoid) | 5-30 | Neither model accurate here |


## 5.2 Mass Conservation


Parse continuity errors from log:
```
time step continuity errors : sum local = 1.23e-07, global = -2.34e-15, cumulative = -5.67e-14
```

| Metric | Acceptable |
|--------|-----------|
| sum local | < 1e-4 (typical: 1e-6 to 1e-8) |
| global | < 1e-10 (should be near machine precision) |
| cumulative | Should not grow unbounded |


## 5.3 Residual Convergence Criteria


**Steady-state (simpleFoam):**

| Field | Typical target | Tight target |
|-------|---------------|-------------|
| p | initial residual < 1e-4 | < 1e-5 |
| U | initial residual < 1e-4 | < 1e-5 |
| k, epsilon, omega | initial residual < 1e-4 | < 1e-5 |

Convergence: residuals should decrease monotonically. Oscillating residuals indicate numerical issues.

**Transient:** Final residuals within each time step should reach solver tolerance. Initial residuals should not grow over successive time steps.


## 5.4 Benchmark Cases


Available locally at `/usr/lib/openfoam/openfoam2312/tutorials/`:

**Lid-Driven Cavity (icoFoam):**
```bash
# Path: tutorials/incompressible/icoFoam/cavity/cavity/
blockMesh && icoFoam
# Validates: PISO, basic BCs
# Expected: single primary vortex at Re=100, compare with Ghia et al. (1982)
```

**Backward-Facing Step — pitzDaily (simpleFoam):**
```bash
# Path: tutorials/incompressible/simpleFoam/pitzDaily/
blockMesh && simpleFoam
# Validates: SIMPLE, k-epsilon turbulence, wall functions
# Expected: reattachment at ~6-7 step heights downstream
```

**Dam Break (interFoam):**
```bash
# Path: tutorials/multiphase/interFoam/laminar/damBreak/damBreak/
blockMesh && setFields && interFoam
# Validates: VOF, free surface, interFoam
```

**motorBike (simpleFoam + snappyHexMesh):**
```bash
# Path: tutorials/incompressible/simpleFoam/motorBike/
# Full parallel workflow with snappyHexMesh
# Validates: complex geometry meshing, parallel execution, force coefficients
```


## 5.5 Function Objects for Monitoring


Include in controlDict `functions {}`:

| Name | Purpose |
|------|---------|
| `#includeFunc yPlus` | Wall y+ field |
| `#includeFunc CourantNo` | Courant number field |
| `#includeFunc fieldMinMax` | Min/max of all fields |
| `#includeFunc solverInfo` | Residual data per timestep |
| `#includeFunc wallShearStress` | Wall shear stress |
| `#includeFunc vorticity` | Vorticity field |
| `#includeFunc Q` | Q criterion for vortex identification |

All function object templates at: `/usr/lib/openfoam/openfoam2312/etc/caseDicts/postProcessing/`


## 5.6 Export for ParaView


```bash
foamToVTK                                # all times -> VTK/ directory
foamToVTK -latestTime                    # latest only
foamToVTK -fields '(U p)'               # specific fields
foamToVTK -time '100:200'               # time range
```

---
