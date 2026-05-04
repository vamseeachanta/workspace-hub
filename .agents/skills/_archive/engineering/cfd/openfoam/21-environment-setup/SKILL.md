---
name: openfoam-21-environment-setup
description: 'Sub-skill of openfoam: 2.1 Environment Setup (+6).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 2.1 Environment Setup (+6)

## 2.1 Environment Setup


```bash
source /usr/lib/openfoam/openfoam2312/etc/bashrc
```


## 2.2 Serial Workflow


```bash
# 1. Generate mesh
blockMesh

# 2. Check mesh quality
checkMesh
checkMesh -allTopology -allGeometry          # comprehensive

# 3. Initialize flow (optional, helps convergence)
potentialFoam -writephi

# 4. Run solver
simpleFoam > log.simpleFoam 2>&1             # steady-state
pimpleFoam > log.pimpleFoam 2>&1             # transient
interFoam > log.interFoam 2>&1               # multiphase
icoFoam > log.icoFoam 2>&1                   # laminar transient

# 5. Post-process
simpleFoam -postProcess -func yPlus -latestTime
foamToVTK -latestTime                        # export for ParaView
foamLog log.simpleFoam                       # extract residuals to logs/
```


## 2.3 Parallel Workflow


```bash
# 1. Decompose
decomposePar

# 2. Run in parallel
mpirun -np 4 simpleFoam -parallel > log.simpleFoam 2>&1

# 3. Reconstruct
reconstructPar -latestTime                   # latest time only
reconstructPar                               # all times

# 4. Cleanup processor directories (after reconstruction)
rm -rf processor*
```


## 2.4 Complex Geometry Workflow (snappyHexMesh)


```bash
surfaceFeatureExtract                        # extract feature edges from STL
blockMesh                                    # background mesh
decomposePar
mpirun -np 6 snappyHexMesh -overwrite -parallel
mpirun -np 6 potentialFoam -writephi -parallel
mpirun -np 6 simpleFoam -parallel > log.simpleFoam 2>&1
reconstructPar -latestTime
```


## 2.5 Multiphase Workflow (interFoam)


```bash
blockMesh
setFields                                    # initialize alpha field from setFieldsDict
interFoam > log.interFoam 2>&1
```


## 2.6 Solver Selection Guide


| Scenario | Solver | Algorithm |
|----------|--------|-----------|
| Steady incompressible RANS | simpleFoam | SIMPLE |
| Transient incompressible | pimpleFoam | PIMPLE |
| Transient laminar | icoFoam | PISO |
| VOF multiphase | interFoam | PIMPLE |
| Potential flow init | potentialFoam | — |
| Compressible | rhoSimpleFoam | SIMPLE |
| Buoyant convection | buoyantSimpleFoam | SIMPLE |


## 2.7 Key CLI Flags


| Flag | Purpose |
|------|---------|
| `-case <dir>` | Specify case directory |
| `-parallel` | Run in parallel (after decomposePar) |
| `-postProcess` | Execute function objects only |
| `-latestTime` | Process latest time directory only |
| `-overwrite` | Overwrite existing mesh (snappyHexMesh) |
| `-writephi` | Write flux field (potentialFoam) |
| `-dry-run` | Check setup without running |

---
