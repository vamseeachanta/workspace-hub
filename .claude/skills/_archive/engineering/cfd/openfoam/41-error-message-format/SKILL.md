---
name: openfoam-41-error-message-format
description: 'Sub-skill of openfoam: 4.1 Error Message Format (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 4.1 Error Message Format (+2)

## 4.1 Error Message Format


```
--> FOAM FATAL ERROR:
    <description>
    From function <Class>::<method>
    in file <source.C> at line <N>.
FOAM exiting
```


## 4.2 Common Failures and Fixes


**1. Floating Point Exception (exit code 136)**

| Cause | Diagnosis | Fix |
|-------|-----------|-----|
| Courant number too high | Check `Courant Number max:` in log | Enable `adjustTimeStep yes; maxCo 1;` or reduce `deltaT` |
| Poor mesh quality | Run `checkMesh -allTopology -allGeometry` | Fix cells with non-orthogonality > 70, negative volumes |
| Zero/negative k or epsilon | Check 0/ initial values | Set k > 0 and epsilon > 0 everywhere |
| Bad turbulence initialization | Residuals blow up immediately | Start laminar, then switch to turbulent |

**2. GAMG Solver Divergence**

Symptoms: p residuals stuck near 1.0, or oscillating without decreasing.

| Cause | Fix |
|-------|-----|
| Mesh too coarse | Refine mesh at critical regions |
| Bad relaxation factors | Reduce: p from 0.3 to 0.2, U from 0.7 to 0.5 |
| Non-orthogonal mesh | Increase `nNonOrthogonalCorrectors` to 1-3 |
| GAMG agglomeration failure | Switch to `solver PCG; preconditioner DIC;` for p |

**3. Missing Field/File**

```
FOAM FATAL IO ERROR: cannot find file ... /0/k
```

Fix: ensure all fields required by the turbulence model exist in 0/. See table in Section 1.6.

**4. Boundary Condition Mismatch**

```
FOAM FATAL ERROR: patch type 'xxx' not constraint type ... for patch yyy
```

Fix: patch types in 0/ files must match boundary types in `constant/polyMesh/boundary`. If mesh defines `empty`, all field files must use `empty` for that patch.

**5. Courant Number Blowup (transient)**

```
Courant Number mean: 0.5 max: 150.3
```

| Solver | Acceptable maxCo |
|--------|-------------------|
| icoFoam (PISO) | < 1 (strict) |
| interFoam (VOF) | maxCo < 1, maxAlphaCo < 1 |
| pimpleFoam (nOuterCorrectors > 1) | up to 5-10 |

**6. Convergence Stall (simpleFoam)**

Residuals plateau or oscillate without decreasing.

| Action | How |
|--------|-----|
| Reduce relaxation | U: 0.5-0.7, p: 0.2-0.3 |
| Enable consistent SIMPLE | `consistent yes;` in SIMPLE dict |
| Initialize with potentialFoam | `potentialFoam -writephi` before simpleFoam |
| Check BCs | Ensure mass balance (inlet flux = outlet flux) |

**7. Out of Memory (exit code 137)**

| Action | How |
|--------|-----|
| Reduce mesh | Coarsen or reduce refinement levels |
| Use parallel | `decomposePar` + `mpirun -np N` distributes memory |
| Use binary write | `writeFormat binary;` in controlDict |
| Increase swap | System-level: `sudo fallocate -l 8G /swapfile` |

**8. Parallel Decomposition Errors (exit code 255)**

| Symptom | Fix |
|---------|-----|
| `numberOfSubdomains` mismatch | Must match `-np N` in mpirun |
| Missing processor directories | Run `decomposePar` first |
| Inconsistent mesh across processors | Re-run `decomposePar` |

**9. snappyHexMesh Failures**

| Symptom | Fix |
|---------|-----|
| Empty mesh after castellated step | Check `locationInMesh` is inside domain, not inside geometry |
| Feature edge artifacts | Increase `nFeatureSnapIter` to 10-20 |
| Layer addition failure | Reduce `nSurfaceLayers`, increase `minThickness` |
| STL not found | Check path in `geometry {}` block, use `triSurfaceMesh` type |

**10. Dimension Mismatch**

```
FOAM FATAL ERROR: dimensions not compatible
```

Fix: check `dimensions` line in 0/ field files against the reference table (Section 1.8). Common mistake: using absolute pressure dimensions `[1 -1 -2 0 0 0 0]` instead of kinematic `[0 2 -2 0 0 0 0]` for incompressible solvers.


## 4.3 Mesh Quality Thresholds


| Metric | OK | Warning | Fail |
|--------|-----|---------|------|
| Non-orthogonality max | < 65 | 65-80 | > 80 |
| Skewness | < 4 | 4-10 | > 10 |
| Aspect ratio | < 100 | 100-1000 | > 1000 |
| Min volume | > 0 | near 0 | < 0 (inverted) |
| Min determinant | > 0.001 | 0.0001-0.001 | < 0 |

---
