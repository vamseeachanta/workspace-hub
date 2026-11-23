---
name: openfoam-15-fvsolution
description: 'Sub-skill of openfoam: 1.5 fvSolution (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1.5 fvSolution (+3)

## 1.5 fvSolution


**SIMPLE (steady-state):**
```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        smoother        GaussSeidel;
    }
    "(U|k|epsilon|omega|f|v2)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      yes;
    residualControl
    {
        p               1e-2;
        U               1e-3;
        "(k|epsilon|omega)" 1e-3;
    }
}
relaxationFactors
{
    equations
    {
        U               0.9;
        ".*"            0.9;
    }
}
```

**PIMPLE (transient):**
```cpp
solvers
{
    p     { solver GAMG; tolerance 1e-7; relTol 0.01; smoother DICGaussSeidel; }
    pFinal { $p; relTol 0; }
    "(U|k|epsilon)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }
    "(U|k|epsilon)Final" { $U; relTol 0; }
}
PIMPLE
{
    nNonOrthogonalCorrectors 0;
    nCorrectors         2;
}
```

**PISO (laminar transient):**
```cpp
solvers
{
    p     { solver PCG; preconditioner DIC; tolerance 1e-06; relTol 0.05; }
    pFinal { $p; relTol 0; }
    U     { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0; }
}
PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
```

**Available linear solvers:** GAMG, PCG, PBiCGStab, smoothSolver.
**Available smoothers:** GaussSeidel, symGaussSeidel, DIC, DILU, DICGaussSeidel.


## 1.6 transportProperties and turbulenceProperties


**Single-phase incompressible:**
```cpp
// constant/transportProperties
transportModel  Newtonian;
nu              1e-05;          // kinematic viscosity [m^2/s]
```

**Turbulence model selection:**
```cpp
// constant/turbulenceProperties
simulationType      RAS;        // or laminar, LES
RAS
{
    RASModel        kEpsilon;   // kOmegaSST, realizableKE, SpalartAllmaras
    turbulence      on;
    printCoeffs     on;
}
```

**Required 0/ fields by turbulence model:**

| Model | Fields needed in 0/ |
|-------|---------------------|
| laminar | U, p |
| kEpsilon | U, p, k, epsilon, nut |
| kOmegaSST | U, p, k, omega, nut |
| SpalartAllmaras | U, p, nuTilda, nut |
| interFoam (add) | alpha.water, p_rgh |


## 1.7 Boundary Conditions


**Velocity (U) — dimensions [0 1 -1 0 0 0 0]:**

| Patch | BC type | Value |
|-------|---------|-------|
| Inlet (fixed) | `fixedValue` | `uniform (10 0 0)` |
| Outlet | `zeroGradient` | — |
| Wall (no-slip) | `noSlip` | — |
| 2D front/back | `empty` | — |
| Symmetry | `symmetry` | — |

**Pressure (p) — dimensions [0 2 -2 0 0 0 0] (kinematic):**

| Patch | BC type | Value |
|-------|---------|-------|
| Inlet | `zeroGradient` | — |
| Outlet (fixed) | `fixedValue` | `uniform 0` |
| Wall | `zeroGradient` | — |
| 2D front/back | `empty` | — |

**Turbulence fields — wall functions:**

| Field | Wall BC | Inlet BC | Outlet BC |
|-------|---------|----------|-----------|
| k | `kqRWallFunction` | `fixedValue` | `zeroGradient` |
| epsilon | `epsilonWallFunction` | `fixedValue` | `zeroGradient` |
| omega | `omegaWallFunction` | `fixedValue` | `zeroGradient` |
| nut | `nutkWallFunction` | `calculated` | `calculated` |


## 1.8 Dimension Vectors Reference


Format: `[kg m s K mol A cd]`

| Field | Dimensions |
|-------|-----------|
| U (velocity) | `[0 1 -1 0 0 0 0]` |
| p (kinematic) | `[0 2 -2 0 0 0 0]` |
| k | `[0 2 -2 0 0 0 0]` |
| epsilon | `[0 2 -3 0 0 0 0]` |
| omega | `[0 0 -1 0 0 0 0]` |
| nut, nu | `[0 2 -1 0 0 0 0]` |
| alpha.water | `[0 0 0 0 0 0 0]` |
