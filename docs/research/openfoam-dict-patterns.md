# OpenFOAM Dict File Patterns

> Status: Research completed 2026-02-24
> Target: ESI v2312 (installed on ace-linux-2)
> WRK: WRK-343 (feeds WRK-047 Phase 1 template generation)

## Overview

This document catalogs the dict file patterns required for WRK-047 Phase 1 template
generation, cross-referenced against the YAML config schema from the July 2025 technical
spec. For each dict file: boilerplate sections (identical across cases) vs case-specific
sections (driven by YAML config) are identified.

---

## Universal Header (all dict files)

All OpenFOAM dict files begin with a `FoamFile` header. This is 100% boilerplate
except for the `object` field:

```c++
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;   // ← varies per dict file
}
```

**Jinja2 template variable:** `{{ object_name }}`

---

## 1. blockMeshDict

### Purpose
Generates the background hex mesh (Cartesian block mesh). Required for all cases.
For hull analysis: creates the outer domain (wind tunnel / towing tank shape).

### Boilerplate vs Case-specific

| Section | Type | Notes |
|---------|------|-------|
| FoamFile header | Boilerplate | object = blockMeshDict |
| `scale` | Boilerplate | Always 1 for SI units |
| `vertices` | **Case-specific** | Driven by domain dimensions |
| `blocks` | **Case-specific** | Driven by cell count targets |
| `edges` | Boilerplate | Empty `()` for straight edges |
| `boundary` | **Case-specific** | Patch names and face connectivity |
| `mergePatchPairs` | Boilerplate | Empty `()` unless using multi-block |

### Template (annotated)

```c++
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale 1;   // all coordinates in metres

// Domain: xMin xMax yMin yMax zMin zMax
// Typical hull analysis: bow upstream, stern downstream
// Rule of thumb: 5L upstream, 10L downstream, 3B lateral, 3D depth
// where L=ship length, B=beam, D=draft

vertices
(
    // bottom face (z = {{ z_min }})
    ( {{ x_min }} {{ y_min }} {{ z_min }} )   // 0
    ( {{ x_max }} {{ y_min }} {{ z_min }} )   // 1
    ( {{ x_max }} {{ y_max }} {{ z_min }} )   // 2
    ( {{ x_min }} {{ y_max }} {{ z_min }} )   // 3
    // top face (z = {{ z_max }})
    ( {{ x_min }} {{ y_min }} {{ z_max }} )   // 4
    ( {{ x_max }} {{ y_min }} {{ z_max }} )   // 5
    ( {{ x_max }} {{ y_max }} {{ z_max }} )   // 6
    ( {{ x_min }} {{ y_max }} {{ z_max }} )   // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7)
    ( {{ nx }} {{ ny }} {{ nz }} )
    simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {
        type patch;
        faces ((0 4 7 3));
    }
    outlet
    {
        type patch;
        faces ((1 2 6 5));
    }
    bottom
    {
        type wall;
        faces ((0 1 2 3));
    }
    top
    {
        type patch;
        faces ((4 5 6 7));
    }
    side1
    {
        type symmetryPlane;
        faces ((0 1 5 4));
    }
    side2
    {
        type symmetryPlane;
        faces ((3 7 6 2));
    }
);

mergePatchPairs ();

// ************************************************************************* //
```

### YAML → blockMeshDict mapping

From July 2025 tech spec YAML:
```yaml
mesh:
  base_cell_size: 0.5      → nx = domain_x / cell_size (rounded)
  # domain derived from geometry
```

From WRK-047 DomainConfig model:
```python
# Automatic domain sizing (Phase 2 domain_builder.py)
x_upstream   = 5.0 * hull_length        # 5L upstream
x_downstream = 10.0 * hull_length       # 10L downstream
y_lateral    = 3.0 * hull_beam          # 3B each side
z_depth      = 3.0 * hull_draft         # 3D below keel
z_above      = 2.0 * hull_draft         # freeboard
```

---

## 2. snappyHexMeshDict

### Purpose
Refines the background mesh around complex geometry (hull STL). The most complex dict;
controls 3 sequential operations: castellated mesh, snapping, layer addition.

### Boilerplate vs Case-specific

| Section | Type | Notes |
|---------|------|-------|
| FoamFile header | Boilerplate | |
| `castellatedMesh/snap/addLayers` flags | Boilerplate | All true for hull analysis |
| `geometry {}` | **Case-specific** | STL file name and patch name |
| `castellatedMeshControls.maxLocalCells` | Boilerplate | 1e6 default |
| `castellatedMeshControls.maxGlobalCells` | **Case-specific** | Scales with mesh size target |
| `castellatedMeshControls.refinementSurfaces` | **Case-specific** | Surface refinement levels |
| `castellatedMeshControls.refinementRegions` | **Case-specific** | Wake region, free surface |
| `castellatedMeshControls.locationInMesh` | **Case-specific** | Must be in fluid, not in hull |
| `snapControls` | Boilerplate | Standard values work for most cases |
| `addLayersControls.layers` | **Case-specific** | Hull patch name, n layers |
| `addLayersControls.expansionRatio` | Boilerplate / Semi | Usually 1.3 |
| `meshQualityControls` | Boilerplate | Standard values |

### Template (condensed — key case-specific sections)

```c++
FoamFile { ... object snappyHexMeshDict; }

castellatedMesh true;
snap            true;
addLayers       true;

geometry
{
    {{ stl_filename }}     // e.g., hull.stl
    {
        type triSurfaceMesh;
        name {{ geometry_name }};   // e.g., hull
    }
    {% if wake_box is defined %}
    wakeBox
    {
        type searchableBox;
        min ( {{ wake_box.x_min }} {{ wake_box.y_min }} {{ wake_box.z_min }} );
        max ( {{ wake_box.x_max }} {{ wake_box.y_max }} {{ wake_box.z_max }} );
    }
    {% endif %}
}

castellatedMeshControls
{
    maxLocalCells        1000000;
    maxGlobalCells       {{ max_global_cells | default(2000000) }};
    minRefinementCells   10;
    maxLoadUnbalance     0.10;
    nCellsBetweenLevels  {{ n_cells_between_levels | default(3) }};
    features ();
    refinementSurfaces
    {
        {{ geometry_name }}
        {
            level ( {{ surface_refine_min }} {{ surface_refine_max }} );
        }
    }
    refinementRegions
    {
        {% if wake_box is defined %}
        wakeBox { mode inside; levels ((1 {{ wake_refine_level }})); }
        {% endif %}
    }
    locationInMesh ( {{ fluid_point.x }} {{ fluid_point.y }} {{ fluid_point.z }} );
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
    layers
    {
        {{ geometry_name }}
        {
            nSurfaceLayers {{ n_surface_layers | default(3) }};
        }
    }
    expansionRatio          {{ expansion_ratio | default(1.3) }};
    finalLayerThickness     0.3;
    minThickness            0.1;
    nGrow                   0;
    featureAngle            60;
    nRelaxIter              3;
    nSmoothSurfaceNormals   1;
    nSmoothNormals          3;
    nSmoothThickness        10;
    maxFaceThicknessRatio   0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle      90;
    nBufferCellsNoExtrude   0;
    nLayerIter              50;
}

meshQualityControls
{
    maxNonOrtho         65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave          80;
    minVol              1e-13;
    minTetQuality       1e-15;
    minArea             -1;
    minTwist            0.05;
    minDeterminant      0.001;
    minFaceWeight       0.05;
    minVolRatio         0.01;
    minTriangleTwist    -1;
    nSmoothScale        4;
    errorReduction      0.75;
}

writeFlags      ( scalarLevels layerSets layerFields );
mergeTolerance  1e-6;
```

### YAML → snappyHexMeshDict mapping

```yaml
mesh:
  type: "snappyHexMesh"         → castellatedMesh/snap/addLayers = true
  base_cell_size: 0.5           → used to compute locationInMesh offset
  refinement_levels:
    surface: 2                  → level (2 3)  # min and max
    wake: 1                     → wakeBox refinement level
  layers:
    n_layers: 5                 → nSurfaceLayers 5
    expansion_ratio: 1.2        → expansionRatio 1.2
```

---

## 3. controlDict

### Purpose
Master simulation control: solver selection, time stepping, output frequency,
and function objects (forces, probes, sampling).

### Boilerplate vs Case-specific

| Key | Type | Notes |
|-----|------|-------|
| `application` | **Case-specific** | simpleFoam / interFoam / pimpleFoam |
| `startFrom/startTime` | Boilerplate | `latestTime` or `0` |
| `stopAt/endTime` | **Case-specific** | Iterations or simulation time |
| `deltaT` | **Case-specific** | 1 (steady) or time-step (transient) |
| `writeControl/writeInterval` | **Case-specific** | Based on output frequency |
| `purgeWrite` | Semi | 0 (keep all) or N for disk management |
| `writeFormat/writePrecision` | Boilerplate | `ascii 6` or `binary` |
| `runTimeModifiable` | Boilerplate | `true` |
| `functions {}` | **Case-specific** | forces, probes, fieldAverage |

### Template

```c++
FoamFile { ... object controlDict; }

application     {{ application }};       // simpleFoam / interFoam / pimpleFoam

startFrom       latestTime;
startTime       0;

stopAt          endTime;
endTime         {{ end_time }};          // iterations (steady) or seconds (transient)

deltaT          {{ delta_t | default(1) }};

writeControl    timeStep;
writeInterval   {{ write_interval | default(100) }};

purgeWrite      0;

writeFormat     ascii;
writePrecision  6;
writeCompression off;

timeFormat      general;
timePrecision   6;

runTimeModifiable true;

{% if forces_patches %}
functions
{
    forces
    {
        type            forces;
        libs            ("libforces.so");
        patches         ( {{ forces_patches | join(' ') }} );
        rho             rhoInf;
        rhoInf          {{ fluid_density | default(1025) }};
        CofR            ( {{ cofr.x | default(0) }} {{ cofr.y | default(0) }} {{ cofr.z | default(0) }} );
        writeControl    timeStep;
        writeInterval   {{ write_interval | default(100) }};
    }
}
{% endif %}
```

---

## 4. fvSchemes

### Purpose
Numerical discretisation schemes for all derivative operations (gradients,
divergence, Laplacian, time derivatives). Controls numerical accuracy and stability.

### Boilerplate level
**High boilerplate** — standard RANS settings work for most incompressible cases.
Only the `div(phi,U)` and time scheme change between solver types.

### Template

```c++
FoamFile { ... object fvSchemes; }

{% if transient %}
ddtSchemes    { default Euler; }
{% else %}
ddtSchemes    { default steadyState; }
{% endif %}

gradSchemes
{
    default         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;
}

divSchemes
{
    default         none;

    {% if transient %}
    div(phi,U)      Gauss linearUpwindV grad(U);
    div(phi,alpha)  Gauss interfaceCompression van Leer 1;
    {% else %}
    div(phi,U)      Gauss linearUpwindV grad(U);
    {% endif %}

    div(phi,k)      Gauss linearUpwind default;
    div(phi,omega)  Gauss linearUpwind default;
    div(phi,epsilon) Gauss linearUpwind default;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes  { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes     { default corrected; }
```

---

## 5. fvSolution

### Purpose
Linear solver settings and algorithm control (SIMPLE for steady-state,
PISO/PIMPLE for transient). Controls convergence criteria and relaxation.

### Template

```c++
FoamFile { ... object fvSolution; }

solvers
{
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }
    {% if transient %}
    pFinal
    {
        $p;
        relTol 0;
    }
    {% endif %}

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-08;
        relTol          0.1;
    }
    k
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-08;
        relTol          0.1;
    }
    omega
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-08;
        relTol          0.1;
    }
    {% if vof %}
    alpha.water
    {
        nAlphaCorr      2;
        nAlphaSubCycles 1;
        cAlpha          1;
    }
    {% endif %}
}

{% if transient %}
PIMPLE
{
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 0;
}
{% else %}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent          yes;
    residualControl
    {
        p               {{ p_residual | default('1e-4') }};
        U               {{ u_residual | default('1e-4') }};
        k               {{ k_residual | default('1e-4') }};
        omega           {{ omega_residual | default('1e-4') }};
    }
}
relaxationFactors
{
    equations { U 0.9; k 0.7; omega 0.7; }
}
{% endif %}
```

---

## 6. transportProperties

### Purpose
Fluid physical properties (viscosity, density). Single-phase for simpleFoam;
two-phase block for interFoam.

### Template (single-phase, simpleFoam)

```c++
FoamFile { ... object transportProperties; }

transportModel  Newtonian;
nu              {{ kinematic_viscosity | default('1.0e-6') }};   // m2/s (seawater ≈ 1e-6)
```

### Template (two-phase, interFoam)

```c++
FoamFile { ... object transportProperties; }

phases (water air);

water
{
    transportModel  Newtonian;
    nu              {{ water_nu | default('1.0e-6') }};
    rho             {{ water_rho | default(1025) }};
}

air
{
    transportModel  Newtonian;
    nu              {{ air_nu | default('1.48e-5') }};
    rho             {{ air_rho | default(1.2) }};
}

sigma           {{ surface_tension | default(0.07) }};   // N/m
```

### YAML → transportProperties mapping

```yaml
physics:
  fluid_properties:
    density: 1025.0        → rho = 1025.0 (seawater)
    viscosity: 1.0e-6      → nu = 1.0e-6 (kinematic)
```

---

## 7. turbulenceProperties

### Purpose
RANS turbulence model selection. Boilerplate structure; only model name varies.

### Template (ESI v2312 syntax)

```c++
FoamFile { ... object turbulenceProperties; }

simulationType  RAS;

RAS
{
    RASModel        {{ turbulence_model | default('kOmegaSST') }};
    turbulence      on;
    printCoeffs     on;
}
```

**Supported models for marine applications:**
- `kOmegaSST` — recommended for hull resistance (adverse pressure gradients)
- `kEpsilon` — pitzDaily default; good for free-stream turbulence
- `realizableKE` — better for separated flows
- `Smagorinsky` — for LES (transient, high-resolution mesh required)
- `laminar` — for low-Re cases (cavity tutorial)

---

## 8. decomposeParDict

### Purpose
Controls parallel decomposition of the domain. Required for snappyHexMesh and
parallel solver runs.

### Template

```c++
FoamFile { ... object decomposeParDict; }

numberOfSubdomains  {{ n_cores | default(4) }};

method  scotch;   // automatic load balancing, no geometry info needed

// scotch requires no additional parameters
scottCoeffs {}
```

### Notes
- `scotch` is the recommended default (automatic, no geometry input needed)
- `simple` (geometric decomposition) and `hierarchical` are alternatives
- `numberOfSubdomains` should match available CPU cores on ace-linux-2
- Run `lscpu | grep "^CPU(s)"` on ace-linux-2 to determine core count

---

## Initial Condition Files (0/ directory)

### U (velocity)

```c++
FoamFile { ... class volVectorField; object U; }
dimensions      [0 1 -1 0 0 0 0];   // m/s
internalField   uniform ( {{ U_inlet }} 0 0 );

boundaryField
{
    inlet       { type fixedValue; value $internalField; }
    outlet      { type zeroGradient; }
    hull        { type noSlip; }
    top         { type slip; }
    bottom      { type slip; }
    side1       { type slip; }
    side2       { type slip; }
}
```

### p (pressure)

```c++
FoamFile { ... class volScalarField; object p; }
dimensions      [0 2 -2 0 0 0 0];   // m2/s2 (kinematic pressure = p/rho)
internalField   uniform 0;

boundaryField
{
    inlet       { type zeroGradient; }
    outlet      { type fixedValue; value uniform 0; }
    hull        { type zeroGradient; }
    top         { type zeroGradient; }
    bottom      { type zeroGradient; }
    side1       { type zeroGradient; }
    side2       { type zeroGradient; }
}
```

### k and omega (kOmegaSST turbulence)

```c++
// k — turbulent kinetic energy [m2/s2]
// Inlet: k = 1.5 * (U * I)^2  where I = turbulence intensity (0.05 typical)
FoamFile { ... class volScalarField; object k; }
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform {{ k_inlet | default('0.1') }};

boundaryField
{
    inlet       { type turbulentIntensityKineticEnergyInlet; intensity 0.05; value $internalField; }
    outlet      { type zeroGradient; }
    hull        { type kqRWallFunction; value $internalField; }
    ...
}
```

---

## YAML Config Schema → Dict File Mapping Summary

Cross-reference against July 2025 technical spec YAML schema:

| YAML key | Dict file | OpenFOAM key |
|----------|-----------|-------------|
| `case_name` | all | FoamFile object names, directory name |
| `geometry.file` | snappyHexMeshDict | geometry block STL filename |
| `mesh.type` | (selects blockMesh vs snappy) | controlDict application |
| `mesh.base_cell_size` | blockMeshDict | nx/ny/nz via division |
| `mesh.refinement_levels.surface` | snappyHexMeshDict | refinementSurfaces level |
| `mesh.layers.n_layers` | snappyHexMeshDict | nSurfaceLayers |
| `mesh.layers.expansion_ratio` | snappyHexMeshDict | expansionRatio |
| `physics.solver` | controlDict | application |
| `physics.turbulence_model` | turbulenceProperties | RASModel |
| `physics.fluid_properties.density` | transportProperties | rho |
| `physics.fluid_properties.viscosity` | transportProperties | nu |
| `boundary_conditions.inlet` | 0/U, 0/p | inlet patch BCs |
| `simulation.end_time` | controlDict | endTime |
| `simulation.write_interval` | controlDict | writeInterval |
| `simulation.convergence_criteria.residual_target` | fvSolution | residualControl |
| `post_processing.forces.patches` | controlDict functions | patches |

---

## Template Engine Decision: Jinja2 vs Alternatives

### Jinja2 (recommended by WRK-047 Phase 1)
```python
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("templates/"))
template = env.get_template("blockMeshDict.j2")
content = template.render(x_min=-50, x_max=100, nx=60, ...)
```
Pros: Conditional blocks `{% if %}`, loops, filters, whitespace control
Cons: Extra dependency (though already in use elsewhere in digitalmodel)

### String templates / f-strings
Pros: Zero dependencies, immediate
Cons: No conditional logic, ugly for long multi-line dicts, escape issues with `{}`

### Python dataclasses + `__str__`
Pros: Type-safe, testable
Cons: Very verbose, duplicates OpenFOAM syntax in Python strings

**Decision: Jinja2 is correct.** The conditional logic (`{% if vof %}`, `{% if transient %}`)
in the templates above cannot be cleanly expressed in f-strings. Jinja2 is already
available in the Python ecosystem and used in other engineering tooling.

---

*Generated: 2026-02-24 | WRK-343*
