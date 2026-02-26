# OpenFOAM Version Landscape

> Status: Research completed 2026-02-24
> WRK: WRK-343 (feeds WRK-047, WRK-292)

## Overview

OpenFOAM has two major maintained forks with diverging dict syntax and feature sets.
WRK-047 must select one as its primary target for template generation and dict file
construction. This document compares the two forks and recommends a target version.

---

## The Two Forks

### ESI Group — OpenFOAM.com

| Property | Value |
|----------|-------|
| Maintainer | ESI Group (commercial CFD company) |
| Release cadence | ~6-monthly (2212, 2306, 2312, 2406...) |
| Versioning | YYMM (year+month, e.g., v2312 = December 2023) |
| Website | openfoam.com |
| License | GPL v3 |
| Distribution | `.com` apt repos, Docker images |
| Installed on ace-linux-2 | **YES — v2312** |

**Version timeline (recent):**
- v2106 (June 2021)
- v2206 (June 2022)
- v2212 (December 2022)
- v2306 (June 2023)
- v2312 (December 2023) — **installed on ace-linux-2**
- v2406 (June 2024)
- v2412 (December 2024) — latest as of research date

### OpenFOAM Foundation — OpenFOAM.org

| Property | Value |
|----------|-------|
| Maintainer | OpenFOAM Foundation (non-profit) |
| Release cadence | ~yearly |
| Versioning | Integer (v10, v11, v12...) |
| Website | openfoam.org |
| License | GPL v3 |
| Distribution | `.org` apt repos, Docker images |
| Installed on ace-linux-2 | NO |

**Version timeline (recent):**
- v9 (June 2021)
- v10 (July 2022)
- v11 (July 2023)
- v12 (July 2024) — latest stable

---

## Key Dict Syntax Differences

These differences directly affect WRK-047 template generation.

### turbulenceProperties

**ESI v2312 (installed on ace-linux-2):**
```c++
FoamFile { version 2.0; format ascii; class dictionary; object turbulenceProperties; }

simulationType RAS;

RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
```

**Foundation v12:**
```c++
FoamFile { version 2.0; format ascii; class dictionary; object momentumTransport; }

simulationType RAS;

RAS
{
    model           kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
```

**Difference:** Foundation renamed `turbulenceProperties` → `momentumTransport`. The
`RASModel` key is now `model`. WRK-047 templates must generate ESI syntax for ace-linux-2.

---

### transportProperties (single-phase)

**ESI v2312:**
```c++
FoamFile { ... class dictionary; object transportProperties; }

transportModel  Newtonian;
nu              1e-05;          // kinematic viscosity [m2/s]
```

**Foundation v12:**
```c++
FoamFile { ... class dictionary; object physicalProperties; }

viscosityModel  constant;
nu              1e-05;
```

**Difference:** Foundation renamed `transportProperties` → `physicalProperties` in v10+.
The `transportModel` keyword changed to `viscosityModel`.

---

### transportProperties (multiphase / interFoam)

**ESI v2312:**
```c++
phases (water air);

water
{
    transportModel  Newtonian;
    nu              1e-06;
    rho             1000;
}

air
{
    transportModel  Newtonian;
    nu              1.48e-05;
    rho             1;
}

sigma           0.07;    // surface tension [N/m]
```

**Foundation v12:**
Syntax is nearly identical here. Minor differences in keyword ordering.
ESI added `pMin` keyword for pressure limiter support.

---

### controlDict — function objects

**ESI v2312 forces functionObject:**
```c++
functions
{
    forces
    {
        type            forces;
        libs            ("libforces.so");
        patches         (hull);
        rho             rhoInf;
        rhoInf          1025;
        CofR            (0 0 0);
    }
}
```

**Foundation v12:** Identical syntax here. Function object API is well-preserved
between forks for standard objects (forces, fieldAverage, probes).

---

### blockMeshDict — vertices and blocks

Both forks use identical `blockMeshDict` syntax:
```c++
FoamFile { ... class dictionary; object blockMeshDict; }

scale 1;    // or 'convertToMeters 1;' in older versions

vertices
(
    (0 0 0)    // 0
    (1 0 0)    // 1
    (1 1 0)    // 2
    (0 1 0)    // 3
    (0 0 0.1)  // 4
    (1 0 0.1)  // 5
    (1 1 0.1)  // 6
    (0 1 0.1)  // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    movingWall
    {
        type wall;
        faces ((3 7 6 2));
    }
    ...
);
```

**Difference:** ESI uses `scale` keyword; Foundation uses `convertToMeters`. Both
are equivalent. WRK-047 templates should use `scale` for ESI compatibility.

---

### snappyHexMeshDict

Structure is identical between the two forks. This is the most complex dict and
has been stable across both forks for several versions:

```c++
castellatedMesh  true;
snap             true;
addLayers        true;

geometry
{
    hull.stl
    {
        type triSurfaceMesh;
        name hull;
    }
}

castellatedMeshControls
{
    maxLocalCells        1000000;
    maxGlobalCells       2000000;
    minRefinementCells   10;
    maxLoadUnbalance     0.10;
    nCellsBetweenLevels  3;
    features ();
    refinementSurfaces
    {
        hull { level (2 3); }
    }
    refinementRegions {}
    locationInMesh (10.0 0.0 0.0);
    allowFreeStandingZoneFaces true;
}

snapControls
{
    nSmoothPatch    3;
    tolerance       2.0;
    nSolveIter      30;
    nRelaxIter      5;
}

addLayersControls
{
    relativeSizes   true;
    layers { hull { nSurfaceLayers 3; } }
    expansionRatio  1.3;
    finalLayerThickness 0.3;
    minThickness    0.1;
    nGrow           0;
    featureAngle    60;
    nRelaxIter      3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals  3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter      50;
}
```

---

### fvSchemes — Numerical Discretisation

Both forks use the same structure. Typical ESI v2312 RANS settings:
```c++
ddtSchemes    { default Euler; }
gradSchemes   { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwindV grad(U);
    div(phi,k)      Gauss linearUpwind default;
    div(phi,omega)  Gauss linearUpwind default;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
```

---

### fvSolution — Solvers and Algorithms

**ESI v2312 (SIMPLE):**
```c++
solvers
{
    p   { solver GAMG; smoother GaussSeidel; tolerance 1e-06; relTol 0.1; }
    U   { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0.1; }
    k   { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0.1; }
    omega { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0.1; }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent               yes;
    residualControl { p 1e-4; U 1e-4; k 1e-4; omega 1e-4; }
}

relaxationFactors
{
    equations { U 0.9; k 0.7; omega 0.7; }
}
```

---

## Version Recommendation for WRK-047

**Decision: Target ESI v2312 (confirm existing assumption)**

Rationale:
1. **Installed on ace-linux-2** — the target development machine. No version mismatch.
2. **ESI v2306+ assumption in WRK-047** — v2312 is a superset; all v2306 features are present.
3. **Foundation renamed core dict files** — `turbulenceProperties` → `momentumTransport`,
   `transportProperties` → `physicalProperties`. Targeting ESI avoids this complexity.
4. **ESI releases more frequently** — v2312 is newer than Foundation v12 (both 2023-era).
5. **Marine industry adoption** — ESI's wave generation BC extensions (`waveFoam`,
   `olaFlow`) are more commonly distributed for ESI versions.
6. **PyFoam compatibility** — PyFoam 2023.7 (installed) targets ESI versioning scheme.

**Version-safety note for WRK-047 templates:**
- Templates should include `FoamFile { version 2.0; ... }` headers with the `object` field
  matching ESI naming conventions (not Foundation renamed equivalents)
- Add runtime version detection: `foamVersion` environment variable or `$WM_PROJECT_VERSION`
- Document `ESI_v2312+` as the tested/supported target in module README

---

## Upgrade Path Notes

When ace-linux-2 is updated from v2312 to v2406/v2412:
- `blockMeshDict`, `snappyHexMeshDict`, `fvSchemes`, `fvSolution` syntax: unchanged
- `turbulenceProperties`: unchanged (ESI kept the old name)
- `transportProperties`: unchanged (ESI kept the old name)
- `controlDict`: minor additions, backward-compatible

Foundation migration (if ever needed):
- Rename `turbulenceProperties` → `momentumTransport`, update `RASModel` → `model`
- Rename `transportProperties` → `physicalProperties`, update `transportModel` → `viscosityModel`
- WRK-047 Jinja2 templates should use a `foam_variant` parameter to handle this

---

*Generated: 2026-02-24 | WRK-343*
