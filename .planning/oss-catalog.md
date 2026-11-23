# OSS Engineering Software Catalog — Summary

**Date**: 2026-03-26
**Issue**: workspace-hub#1397
**Catalog**: `data/oss-engineering-catalog.yaml`

## Overview

| Domain | Count | Key Tools |
|--------|-------|-----------|
| FEA | 15 | FEniCSx, MOOSE, Kratos, MFEM, Firedrake, scikit-fem, NGSolve, SfePy, OpenSees, Elmer, deal.II, CalculiX, Code_Aster, FreeFEM, OpenRadioss |
| CFD | 10 | OpenFOAM, SU2, PyFR, PhiFlow, Dedalus, JAX-Fluids, AMReX, Code_Saturne, Nektar++, Palabos |
| O&G/Marine | 34 | OpenFAST, Capytaine, MoorDyn, MoorPy, OpenDrift, FLORIS, WISDEM, WEIS, RAFT, PyWake, windpowerlib, WELIB, ROSCO, WOMBAT, OpenOA, FAModel, windIO, pyHAMS, py-fatigue, pyLife, pycatenary, OCEANLYZ, Thetis, Proteus, OSP, DualSPHysics, REEF3D, Nemoh, BEMRosetta, HAMS, OPM, WEC-Sim, MAP++, Ashes* |
| CAD/CAE | 6 | FreeCAD, gmsh, Salome-Meca, OpenSCAD, BRL-CAD |
| GIS | 15 | QGIS, PostGIS, GRASS GIS, GDAL, GeoPandas, Shapely, Rasterio, Fiona, pyproj, PyGMT, Verde, deck.gl, H3, xarray-spatial |
| Doc Intelligence | 5 | docling, marker, surya, unstructured, nougat |
| Data/Workflow | 9 | Prefect, Dagster, Kedro, Airflow, DVC, MLflow, Hamilton, Great Expectations, Pandera |
| Visualization | 13 | ParaView, VTK, PyVista, Plotly, Dash, Panel, Streamlit, Bokeh, meshio, trimesh, Open3D, vedo |
| Data Science | 11 | NumPy, SciPy, pandas, Polars, xarray, Dask, SymPy, Pint, uncertainties, Numba |
| Standards/Codes | 6 | fluids, ht, PyNite, sectionproperties, ANYstructure, PSI |
| **Total** | **117** | |

*Ashes is NOT open-source (proprietary, free for academic use only).

## Already Cloned at /mnt/ace/

| Library | Path | Domain |
|---------|------|--------|
| OpenFAST | `/mnt/ace/openfast` | O&G/Marine |
| Capytaine | `/mnt/ace/capytaine` | O&G/Marine |
| MoorDyn | `/mnt/ace/MoorDyn` | O&G/Marine |
| MoorPy | `/mnt/ace/MoorPy` | O&G/Marine |
| WEC-Sim | `/mnt/ace/WEC-Sim` | O&G/Marine |
| HAMS | `/mnt/ace/HAMS` | O&G/Marine |
| gmsh | `/mnt/ace/gmsh` | CAD/CAE |
| opm-common | `/mnt/ace/opm-common` | O&G/Marine |

**8 of 117 libraries already cloned** (7%).

---

## Delta Summary (2026-03-26)

### Added: 79 new libraries

**FEA (+8)**:
- Kratos Multiphysics — BSD-4, multi-disciplinary simulation, extensive Python interface
- MFEM — BSD-3, LLNL FEM library, pip-installable PyMFEM
- Firedrake — LGPL-3, automated PDE solver with code generation from UFL
- scikit-fem — BSD-3, pure Python FEM assembly, minimal deps
- SfePy — BSD-3, Python-native coupled PDE solver
- NGSolve — LGPL-2.1, multiphysics FEM with built-in Netgen mesher
- FreeFEM — LGPL-3, 2D/3D PDE solver with DSL
- OpenRadioss — AGPL-3, industrial crash/impact explicit FEA

**CFD (+6)**:
- PyFR — BSD-3, high-order flux reconstruction, GPU-accelerated
- Dedalus — GPL-3, spectral PDE framework, symbolic equations
- PhiFlow — MIT, differentiable PDE solving with ML backends
- Code_Saturne — GPL-2, EDF industrial CFD solver
- AMReX — BSD-3, exascale AMR framework with pyAMReX
- JAX-Fluids — GPL-3, fully differentiable compressible CFD in JAX

**O&G/Marine (+24)**:
- RAFT — Apache-2, floating wind turbine frequency-domain dynamics
- WISDEM — Apache-2, wind plant cost-of-energy optimization (NREL)
- WEIS — Apache-2, multi-fidelity floating offshore wind co-design
- WELIB — MIT, wind energy utility library
- ROSCO — Apache-2, reference wind turbine controller
- FLORIS — Apache-2, wind farm wake modeling and optimization
- PyWake — MIT, DTU wind farm wake simulation
- windpowerlib — MIT, wind power output modelling
- WOMBAT — Apache-2, wind farm O&M simulation
- OpenOA — BSD-3, operational wind plant performance assessment
- FAModel — Apache-2, floating wind array modeling
- windIO — Apache-2, standardized wind energy data schemas
- pyHAMS — Apache-2, Python wrapper for HAMS BEM solver
- Nemoh — Apache-2, original open-source BEM code
- BEMRosetta — GPL-3, BEM coefficients viewer/converter
- DualSPHysics — LGPL-2.1, GPU-accelerated SPH for marine
- REEF3D — GPL-3, marine/coastal hydrodynamics CFD
- Thetis — MIT, coastal ocean model on Firedrake
- Proteus — MIT, ERDC coastal engineering toolkit
- py-fatigue — GPL-3, offshore wind fatigue analysis
- pyLife — Apache-2, fatigue and reliability (Bosch Research)
- pycatenary — MIT, catenary equations for mooring design
- OCEANLYZ — MIT, ocean wave spectral analysis
- OSP/libcosim — MPL-2, DNV maritime co-simulation platform

**GIS (+12)**:
- GDAL — MIT, foundational raster/vector format library
- GeoPandas — BSD-3, spatial DataFrames
- Shapely — BSD-3, planar geometry operations
- Rasterio — BSD-3, Pythonic raster data access
- Fiona — BSD-3, Pythonic vector data access
- pyproj — MIT, coordinate transformations
- PyGMT — BSD-3, publication-quality maps
- Verde — BSD-3, spatial gridding with scikit-learn API
- deck.gl/pydeck — MIT, WebGL geospatial visualization
- H3 — Apache-2, hexagonal geospatial indexing
- xarray-spatial — MIT, raster spatial analytics

**Visualization (+13, new domain)**:
- ParaView — BSD-3, industry-standard scientific visualization
- VTK — BSD-3, core 3D rendering engine
- PyVista — MIT, Pythonic VTK wrapper
- Plotly — MIT, interactive browser-based graphing
- Dash — MIT, analytical web applications
- Panel — BSD-3, HoloViz dashboarding framework
- Streamlit — Apache-2, script-to-app framework
- Bokeh — BSD-3, interactive web visualization
- meshio — MIT, 25+ mesh format I/O
- trimesh — MIT, triangular mesh processing
- Open3D — MIT, 3D data processing with GPU
- vedo — MIT, scientific 3D visualization

**Data Science (+11, new domain)**:
- NumPy, SciPy, pandas, Polars, xarray, Dask, SymPy, Pint, uncertainties, Numba

**Standards/Codes (+6, new domain)**:
- PyNite — MIT, structural engineering FEA
- sectionproperties — MIT, cross-section property calculator
- fluids — MIT, piping/fluid dynamics (Crane/API/ASME)
- ht — MIT, heat transfer correlations (TEMA)
- ANYstructure — MIT, DNV-based steel structure design
- PSI — GPL-3, pipe stress analysis (B31.1)

**Data/Workflow (+5)**:
- Dagster — Apache-2, asset-oriented data orchestration
- Kedro — Apache-2, opinionated data science pipelines
- Hamilton — BSD-3, micro-framework for dataflow DAGs
- Great Expectations — Apache-2, data quality validation
- Pandera — MIT, DataFrame validation

### Changed: 0 existing entries modified

### Removed: 0 entries removed

---

## High-Priority Clone Candidates

Libraries recommended for cloning to `/mnt/ace/` (Python API, high integration fit, not yet cloned):

| Library | Domain | License | Why |
|---------|--------|---------|-----|
| OpenDrift | O&G/Marine | GPL-2 | Oil spill & drift modelling, pure Python |
| FEniCSx | FEA | LGPL-3 | Core PDE solver, first-class Python API |
| docling | Doc Intelligence | MIT | 56k stars, broadest document parsing |
| marker | Doc Intelligence | GPL-3 | High-accuracy PDF extraction |
| FLORIS | O&G/Marine | Apache-2 | Wind farm wake optimization |
| RAFT | O&G/Marine | Apache-2 | Floating turbine dynamics |
| WISDEM | O&G/Marine | Apache-2 | Wind plant system design |
| scikit-fem | FEA | BSD-3 | Pure Python FEM, minimal deps |
| meshio | Visualization | MIT | Multi-format mesh I/O glue |
| PyVista | Visualization | MIT | Pythonic 3D visualization |

**Do NOT clone without confirmation.**

---

## Next Steps

1. Clone high-priority candidates to `/mnt/ace/` (pending confirmation)
2. Wire doc-intelligence tools (docling, marker) into extraction pipelines
3. Evaluate Dagster vs Prefect vs Kedro for pipeline orchestration
4. Create digitalmodel adapter modules for P0 libraries
5. Set up DVC for simulation data versioning
6. Integrate standards/codes tools (fluids, ht, sectionproperties) for automated compliance
