---
id: workspace-hub#1397
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1397
title: "Recurring research: open-source engineering software catalog — all domains, download & doc-intelligence"
type: research
status: pending
priority: high
complexity: complex
created_at: "2026-03-25"
target_repos: [workspace-hub, digitalmodel, aceengineer-gis, worldenergydata]
computer: ace-linux-1
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: research
subcategory: open-source-survey
recurring: daily
tags: [doc-intelligence, open-source, catalog, download, recurring]
plan_reviewed: false
plan_approved: false
percent_complete: 0
---

# Research: Open-Source Engineering Software Catalog

## Objective
Survey, index, download, and maintain document intelligence on ALL open-source
libraries and programs relevant to the workspace-hub engineering ecosystem.
Build a living catalog with capabilities, license terms, maturity, and
integration potential. Downloadable artifacts go to `/mnt/ace/<repo-name>/`
per standard layout.

## Scope — Domains to Cover (comprehensive, miss nothing)

### 1. Structural & Mechanical
- **FEA (Finite Element Analysis)** — structural, thermal, multiphysics (FEniCS, CalculiX, Code_Aster, Elmer, MOOSE, deal.II, GetFEM, MFEM, Kratos)
- **Solid Mechanics** — fatigue, fracture, contact, nonlinear (OpenSees, WARP3D)
- **Vibration & Dynamics** — modal analysis, transient, random vibration

### 2. Fluid Mechanics & CFD
- **CFD solvers** — OpenFOAM, SU2, Palabos, Nektar++, PyFR, Basilisk, Gerris
- **Meshing** — gmsh, snappyHexMesh, cfMesh, SALOME, Netgen, TetGen, Triangle
- **Pre/Post-processing** — ParaView, VisIt, PyVista, VTK, Mayavi

### 3. Oil & Gas / Subsea / Marine
- **Pipeline** — flow assurance, erosion, corrosion models
- **Reservoir** — OPM (Open Porous Media), MRST, ResInsight
- **Subsea/Marine** — mooring, risers, VIV, wave loads (OpenFAST, MAP++, MoorDyn)
- **Naval architecture** — stability, resistance, seakeeping

### 4. CAD / CAM / CAE
- **CAD kernels** — OpenCASCADE (OCCT), FreeCAD, CadQuery, Build123d, solvespace
- **CAM / CNC** — LinuxCNC, FreeCAD Path, PyCAM, dxf2gcode
- **CAE integration** — Salome-Meca, PrePoMax, Netgen/NGSolve

### 5. GIS & Geospatial
- **Core** — GDAL/OGR, PROJ, GeoPandas, Shapely, Fiona, Rasterio
- **Visualization** — QGIS, Leaflet, Deck.gl, Kepler.gl, CesiumJS
- **Bathymetry / Terrain** — GMT, GEBCO tools, Whitebox

### 6. Data Science & Numerical
- **Optimization** — SciPy, PuLP, Pyomo, DEAP, Optuna
- **Signal processing** — librosa, scipy.signal, PyWavelets
- **Statistics** — statsmodels, scikit-learn, PyMC
- **Surrogate modeling** — SMT, GPyTorch, BoTorch

### 7. Document Intelligence & Data Extraction
- **PDF extraction** — pdfplumber, camelot, tabula-py, PyMuPDF, marker
- **OCR** — Tesseract, EasyOCR, PaddleOCR, docTR
- **Table detection** — table-transformer, unstructured, deepdoctection

### 8. Workflow & Orchestration
- **Task runners** — Prefect, Airflow, Luigi, Dagster
- **Notebook** — Jupyter, Papermill, nbconvert
- **CLI** — Click, Typer, Rich, Textual

### 9. Standards & Codes
- **API, DNV, ABS, ISO** processing tools
- **Unit conversion** — Pint, unyt, astropy.units
- **Material databases** — MatWeb scrapers, MAST, pymatgen

### 10. Simulation & Multiphysics
- **Coupled solvers** — preCICE, OpenMDAO, Dakota
- **DEM** — LIGGGHTS, Yade, MercuryDPM
- **Electromagnetics** — Palace, Gmsh+GetDP, FEMM, pyEPR

### 11. Visualization & Reporting
- **Plotting** — Matplotlib, Plotly, Bokeh, Altair, HoloViews
- **3D** — Three.js, Blender (bpy), Open3D, trimesh
- **Reporting** — Quarto, Sphinx, MkDocs, WeasyPrint

## For Each Library, Capture

| Field | Description |
|-------|-------------|
| Name | Library/program name |
| URL | Repository or homepage |
| Language | Primary language(s) |
| Capabilities | Core features, domain coverage |
| License | Type + commercial-use implications |
| Maturity | active / maintained / archived / experimental |
| Python API | Bindings available? pip-installable? |
| Downloadable | Yes/No — can we clone/download artifacts? |
| Integration | Fit with digitalmodel, aceengineer-gis, workspace-hub |
| Community | Stars, contributors, last release date |
| Notes | Anything notable (breaking changes, forks, etc.) |

## Download & Document Intelligence Pipeline

For libraries/tools that are downloadable:

1. **Clone/download** to `/mnt/ace/<repo-name>/` following standard layout:
   ```
   /mnt/ace/<repo-name>/
   ├── docs/          # extracted documentation
   ├── projects/      # example projects, tutorials
   └── tests/         # test suites if useful
   ```
2. **Run doc-intelligence** — extract, classify, and promote key docs/tables
   per the standard deep-extraction pipeline (same as WRK-1288/WRK-1353 pattern)
3. **Index** extracted knowledge back into `docs/research/` catalog

## Recurring Schedule (Daily)

Each daily execution should:
1. Check for new releases, new libraries, or newly discovered tools
2. Update the master index with changes (new entries, version bumps, license changes)
3. Flag libraries with license changes, deprecation, or security advisories
4. Download/update any newly qualifying artifacts to `/mnt/ace/`
5. Run doc-intelligence on new downloads
6. Produce a daily delta summary appended to the research log

## Output

- **Master catalog**: `docs/research/open-source-engineering-libs.md`
- **Per-domain indexes**: `docs/research/domains/<domain>.md`
- **Daily deltas**: `docs/research/daily/<YYYY-MM-DD>.md`
- **Download registry**: `docs/research/download-registry.md` (what's at `/mnt/ace/`)
