# OSS Engineering Software Catalog — Summary

**Date**: 2026-03-26
**Issue**: workspace-hub#1397
**Catalog**: `data/oss-engineering-catalog.yaml`

## Overview

| Domain | Count | Key Tools |
|--------|-------|-----------|
| FEA | 7 | FEniCSx, MOOSE, OpenSees, Elmer, deal.II, CalculiX, Code_Aster |
| CFD | 4 | OpenFOAM, SU2, Nektar++, Palabos |
| O&G/Marine | 10 | OpenFAST, Capytaine, MoorDyn, MoorPy, OpenDrift, HAMS, WEC-Sim, OPM, MAP++, Ashes* |
| CAD/CAE | 5 | FreeCAD, gmsh, Salome-Meca, OpenSCAD, BRL-CAD |
| GIS | 3 | QGIS, PostGIS, GRASS GIS |
| Doc Intelligence | 5 | docling, marker, surya, unstructured, nougat |
| Data/Workflow | 4 | Airflow, Prefect, DVC, MLflow |
| **Total** | **38** | |

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

**8 of 38 libraries already cloned** (21%) — all in the O&G/Marine and CAD/CAE domains.

---

## Top 10 for Immediate digitalmodel Integration

Ranked by: Python API quality, pip-installability, domain relevance to offshore/subsea engineering, community maturity, and existing ecosystem fit.

### 1. Capytaine (BEM Hydrodynamics) — ALREADY CLONED
- **Why**: Core hydrodynamic coefficient solver. Pure Python + Fortran backend. pip-installable. Computes added mass, damping, excitation forces for floating structures.
- **Action**: Wire into digitalmodel as hydrodynamics module.

### 2. MoorDyn (Mooring Dynamics) — ALREADY CLONED
- **Why**: Lumped-mass mooring model with Python bindings. Couples with OpenFAST. Essential for mooring analysis in subsea/floating platform design.
- **Action**: Create Python wrapper module in digitalmodel for mooring simulations.

### 3. OpenDrift (Ocean Trajectory Modelling)
- **Why**: Pure Python, pip-installable. Oil spill tracking, environmental dispersion, SAR drift modelling. Direct relevance to O&G operations and environmental compliance.
- **Action**: Clone to `/mnt/ace/opendrift`, integrate as environmental module.

### 4. gmsh (Mesh Generation) — ALREADY CLONED
- **Why**: `pip install gmsh` — excellent Python API. Industry-standard FEA/CFD mesh generator. Required by every simulation workflow.
- **Action**: Already available. Ensure digitalmodel meshing module wraps gmsh API.

### 5. FEniCSx (FEM PDE Solver)
- **Why**: First-class Python API for custom PDE problems. Automatic code generation from variational forms. Enables bespoke structural/thermal analyses.
- **Action**: Clone to `/mnt/ace/dolfinx`, create digitalmodel FEA adapter.

### 6. docling (Document Intelligence)
- **Why**: 56k stars, MIT license, IBM-backed. Converts PDF/DOCX/PPTX to structured data. Essential for extracting data from engineering standards and specifications.
- **Action**: Clone, integrate into doc-intelligence pipeline.

### 7. marker (PDF to Markdown)
- **Why**: 33k stars. High-accuracy PDF extraction. Powers engineering document analysis for standards, datasheets, and technical reports.
- **Action**: Clone, integrate as PDF extraction layer alongside docling.

### 8. DVC (Data Version Control)
- **Why**: Git-like versioning for large engineering datasets, simulation results, and model files. Apache-2.0. pip-installable.
- **Action**: Adopt for versioning simulation inputs/outputs across projects.

### 9. Prefect (Workflow Orchestration)
- **Why**: Modern Pythonic workflow engine. Decorator-based. Lighter than Airflow. Ideal for orchestrating simulation pipelines (mesh → solve → post-process).
- **Action**: Evaluate as pipeline orchestrator for digitalmodel batch workflows.

### 10. OpenFAST (Wind/Marine Turbine Sim) — ALREADY CLONED
- **Why**: Comprehensive aero-hydro-servo-elastic simulation. Python bindings. Critical for offshore wind and floating platform engineering.
- **Action**: Already cloned. Ensure Python bindings are exposed in digitalmodel.

---

## Integration Priority Matrix

| Priority | Library | Python API | pip-install | Already Cloned | Stars |
|----------|---------|-----------|-------------|----------------|-------|
| P0 | Capytaine | native | yes | yes | 206 |
| P0 | MoorDyn | bindings | yes | yes | 96 |
| P0 | gmsh | native | yes | yes | — |
| P1 | OpenDrift | native | yes | no | 300 |
| P1 | FEniCSx | native | yes | no | 1,088 |
| P1 | docling | native | yes | no | 56,556 |
| P1 | marker | native | yes | no | 33,079 |
| P2 | DVC | CLI+API | yes | no | 15,478 |
| P2 | Prefect | native | yes | no | 21,966 |
| P2 | OpenFAST | bindings | partial | yes | 877 |

## Next Steps

1. Clone P1 libraries to `/mnt/ace/`
2. Run doc-intelligence extraction on cloned repos
3. Create digitalmodel adapter modules for P0 libraries
4. Evaluate Prefect vs Airflow for pipeline orchestration
5. Set up DVC for simulation data versioning
