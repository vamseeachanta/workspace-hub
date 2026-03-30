# OSS Catalog Triage — March 2026

> **Issue**: vamseeachanta/workspace-hub#1461
> **Catalog**: `data/oss-engineering-catalog.yaml` (117 libraries, 59 remaining)
> **Date**: 2026-03-29
> **Method**: Web research (GitHub stats, PyPI, docs) — no installations

## Tier Summary

| Tier | Count | Criteria |
|------|-------|----------|
| **1 — Integrate next** | 15 | Actively maintained, pip-installable, directly relevant to offshore/structural/marine |
| **2 — Evaluate later** | 28 | Useful but niche, has system deps, or tangentially relevant |
| **3 — Watch list** | 16 | Experimental, low activity, heavy deps, or foundational (install-on-demand) |

---

## Tier 1 — Integrate Next

| Library | Domain | Stars | Last Active | Install | Relevance | Rationale |
|---------|--------|-------|-------------|---------|-----------|-----------|
| **pycatenary** | O&G/Marine | ~17 | Jan 2026 | 1 | 3 | Pure Python catenary solver for mooring line geometry/tension — zero friction |
| **OCEANLYZ** | O&G/Marine | ~36 | ~2023 | 1 | 3 | Spectral + zero-crossing wave analysis; essential for met-ocean data processing |
| **scikit-fem** | FEA | ~605 | Jan 2026 | 1 | 2 | Pure Python FEM assembler; good for structural prototyping with meshio |
| **FAModel** | O&G/Marine | ~7 | Feb 2025 | 2 | 3 | NREL floating array modeling (RAFT + MoorPy + FLORIS integration) |
| **pyHAMS** | O&G/Marine | ~17 | Sep 2025 | 3 | 3 | Python wrapper for HAMS BEM solver; pairs with RAFT for hull hydrodynamics |
| **BEMRosetta** | O&G/Marine | ~101 | Aug 2025 | 3 | 3 | Cross-format BEM results viewer/converter (Nemoh, WAMIT, Capytaine, Aqwa) |
| **Shapely** | GIS | ~4.1k | Jan 2026 | 1 | 3 | Core planar geometry for site boundaries, exclusion zones, cable routing |
| **pyproj** | GIS | ~1.2k | Aug 2025 | 2 | 3 | CRS transformations essential for all offshore GIS work |
| **Plotly** | Viz | ~17.7k | Active 2026 | 1 | 3 | Interactive plots for load curves, RAO, fatigue — widely used in engineering |
| **trimesh** | Viz | ~3.5k | Mar 2026 | 1 | 3 | Triangular mesh processing for hull geometry, clearance checks |
| **Rasterio** | GIS | ~2.5k | Jan 2026 | 2 | 3 | Bathymetric grids, seabed classification; wraps GDAL with clean Python API |
| **REEF3D** | O&G/Marine | ~121 | Feb 2026 | 3 | 3 | Marine/coastal CFD with wave modeling and moored structure interaction |
| **Pandera** | Data/Workflow | ~4.3k | Mar 2026 | 1 | 2 | DataFrame schema validation for engineering tabular data contracts |
| **WOMBAT** | O&G/Marine | ~29 | Jan 2026 | 1 | 2 | Discrete-event O&M simulation for offshore wind farms |
| **windIO** | O&G/Marine | ~43 | Feb 2026 | 1 | 2 | IEA standardized YAML schema for wind turbine/plant data interoperability |

---

## Tier 2 — Evaluate Later

| Library | Domain | Stars | Last Active | Install | Relevance | Rationale |
|---------|--------|-------|-------------|---------|-----------|-----------|
| **SfePy** | FEA | ~820 | Dec 2025 | 2 | 2 | Coupled PDE framework with homogenization; optional PETSc/MUMPS deps |
| **Code_Saturne** | CFD | ~149 | Feb 2025 | 3 | 3 | EDF industrial CFD; directly applicable to offshore wake/scour but heavy build |
| **GDAL** | GIS | ~5.8k | Active 2026 | 3 | 3 | Foundational raster/vector I/O; needed by Rasterio/Fiona but heavy C deps |
| **Fiona** | GIS | ~1.2k | Sep 2025 | 2 | 2 | Vector file I/O for geohazard, lease boundary, pipeline data |
| **ParaView** | Viz | ~1.5k | Active 2026 | 3 | 3 | Industry-standard FEA/CFD post-processing; heavy install |
| **VTK** | Viz | ~3.1k | Mar 2026 | 3 | 3 | Core 3D rendering underlying ParaView; C++ build required |
| **Open3D** | Viz | ~13k | Active 2026 | 2 | 2 | Point cloud / 3D data processing for LiDAR/sonar scans |
| **vedo** | Viz | ~2.2k | Jun 2025 | 1 | 2 | VTK-based scientific 3D viz with simpler API for notebooks |
| **Dash** | Viz | ~24.3k | Dec 2025 | 1 | 2 | Python-native analytical web apps for engineering dashboards |
| **Panel** | Viz | ~5.6k | Active 2026 | 1 | 2 | HoloViz dashboarding for interactive analysis exploration |
| **Streamlit** | Viz | ~38.1k | Active 2026 | 1 | 2 | Rapid script-to-app for internal engineering tools |
| **Bokeh** | Viz | ~19.5k | Active 2026 | 1 | 2 | Interactive web viz good for time-series metocean monitoring |
| **deck.gl/pydeck** | GIS | ~13.4k | Jan 2026 | 1 | 2 | WebGL geospatial dashboard for fleet/asset visualization |
| **H3** | GIS | ~960 | Oct 2025 | 1 | 2 | Hexagonal spatial indexing for metocean coverage analysis |
| **xarray-spatial** | GIS | ~845 | Dec 2025 | 1 | 2 | Numba-backed raster operations on xarray grids |
| **DualSPHysics** | O&G/Marine | ~662 | May 2025 | 3 | 2 | GPU-accelerated SPH for wave-structure interaction; HPC-only |
| **Thetis** | O&G/Marine | ~80 | Active 2025 | 3 | 2 | Coastal ocean/tidal model on Firedrake; heavy dependency chain |
| **Proteus** | O&G/Marine | ~94 | Sep 2024 | 3 | 2 | ERDC coastal engineering toolkit; very complex build |
| **OpenOA** | O&G/Marine | ~237 | Jan 2026 | 1 | 2 | Operational performance analytics on SCADA data |
| **PyWake** | O&G/Marine | ~83 | Feb 2026 | 1 | 2 | Wake deficit modeling for offshore farm layout optimization |
| **ROSCO** | O&G/Marine | ~161 | Jan 2026 | 2 | 2 | Reference wind turbine controller; relevant for load-case studies |
| **WELIB** | O&G/Marine | ~110 | Active 2026 | 1 | 2 | Wind energy BEM/aeroelastic tools tied to OpenFAST ecosystem |
| **Kedro** | Data/Workflow | ~10.5k | Active 2026 | 1 | 2 | Opinionated pipeline framework for reproducible engineering workflows |
| **Hamilton** | Data/Workflow | ~2.4k | Active 2026 | 1 | 2 | Lightweight function-graph dataflow; lower overhead than Kedro |
| **Great Expectations** | Data/Workflow | ~11.3k | Mar 2025 | 1 | 2 | Data quality assertions on metocean/inspection datasets |
| **Nemoh** | O&G/Marine | ~65 | **Archived** Oct 2024 | 3 | 3 | Original BEM solver; GitHub archived, use Capytaine instead |
| **libcosim/OSP** | O&G/Marine | ~72 | May 2025 | 3 | 2 | DNV FMI co-simulation framework; significant integration effort |
| **Verde** | GIS | ~640 | Jun 2023 | 1 | 2 | Spatial gridding for scattered data; **stale since 2023** |

---

## Tier 3 — Watch List

| Library | Domain | Stars | Last Active | Install | Relevance | Rationale |
|---------|--------|-------|-------------|---------|-----------|-----------|
| **FreeFEM** | FEA | ~906 | Mar 2026 | 3 | 2 | Powerful PDE solver but own DSL, not Python-native |
| **OpenRadioss** | FEA | ~719 | Feb 2026 | 3 | 2 | Explicit FEA (crash/impact); Fortran solver, not a Python library |
| **PyFR** | CFD | ~700 | Aug 2025 | 3 | 2 | High-order GPU CFD; overkill for most offshore work, HPC-dependent |
| **Dedalus** | CFD | ~602 | Jan 2026 | 2 | 1 | Spectral PDE framework; geophysical focus, not offshore engineering |
| **PhiFlow** | CFD | ~1.8k | Mar 2026 | 1 | 1 | Differentiable PDE for ML surrogates, not production CFD |
| **AMReX** | CFD | ~699 | Jan 2026 | 3 | 1 | Exascale AMR framework; research-scale, poor engineering ergonomics |
| **JAX-Fluids** | CFD | ~429 | Active 2025 | 2 | 1 | Differentiable compressible CFD; compressible focus limits offshore use |
| **windpowerlib** | O&G/Marine | ~379 | Sep 2025 | 1 | 1 | Power curve / yield assessment only; tangential to structural work |
| **PSI** | Standards | <50 | ~2021 | 1 | 3 | B31.1 pipe stress; pre-alpha, unmaintained since 2021 |
| **NumPy** | Data Sci | ~31k | Active 2026 | 1 | 3 | Foundational — already installed everywhere |
| **SciPy** | Data Sci | ~14.2k | Active 2026 | 1 | 3 | Foundational — already installed everywhere |
| **pandas** | Data Sci | ~25k | Active 2026 | 1 | 3 | Foundational — already installed everywhere |
| **Polars** | Data Sci | ~37.7k | Active 2026 | 1 | 2 | Rust DataFrame; viable pandas alternative for large datasets |
| **xarray** | Data Sci | ~4.1k | Active 2026 | 1 | 3 | N-D labeled arrays; essential for gridded metocean data |
| **Dask** | Data Sci | ~13.7k | Jan 2026 | 1 | 2 | Parallel/out-of-core for large hindcast datasets |
| **SymPy** | Data Sci | ~14.5k | Active 2025 | 1 | 2 | Symbolic math for deriving structural formulas |
| **uncertainties** | Data Sci | ~615 | Apr 2025 | 1 | 2 | Error propagation for measurement uncertainty |
| **Numba** | Data Sci | ~10.8k | Dec 2025 | 1 | 2 | JIT for tight numerical loops; already well-known |

> **Note**: Data Science libraries (NumPy–Numba) are Tier 3 not because they lack value, but because they are foundational and install-on-demand — no integration work needed.

---

## Top 5 Recommendations for Individual Issues

These Tier 1 libraries have the highest value-to-effort ratio for the offshore/marine engineering workflow:

| Priority | Library | Why |
|----------|---------|-----|
| 1 | **pycatenary** | Pure pip, zero friction, directly solves mooring line geometry — can integrate today |
| 2 | **scikit-fem** | Pure Python FEM assembly; enables rapid structural prototyping without heavy solvers |
| 3 | **BEMRosetta** | QA tool for hydrodynamic coefficients across solvers (Capytaine, WAMIT, Aqwa) |
| 4 | **Shapely** | Core geometry engine needed by multiple downstream tools (site layout, cable routing) |
| 5 | **trimesh** | Mesh processing for hull geometry, subsea equipment, collision/clearance analysis |

---

## Caution Flags

- **Nemoh** — GitHub archived Oct 2024; redirect to Capytaine (already in catalog)
- **Verde** — No activity since Jun 2023; treat as maintenance-only
- **PSI** — Pre-alpha, last commit ~2021; not production-usable
- **pyproj** — Now requires Python >=3.11 (not 3.10)
- **SciPy** 1.16+ — Now requires Python >=3.11; pin to 1.15.x for 3.10 support
