# Capytaine BEM Evaluation — Hull Mesh Hydrodynamic Analysis

**Date:** 2026-03-31
**Issue:** vamseeachanta/workspace-hub#1464
**Evaluated by:** Research agent (web research + live installation verification)

---

## Summary

Capytaine 2.3.1 is a Python-based linear potential flow BEM solver, rewritten from the Fortran-based Nemoh. It computes added mass, radiation damping, and wave excitation forces for floating bodies in frequency domain. Installed and verified on dev-secondary at `/mnt/local-analysis/capytaine-env` (Python 3.12). Full radiation + diffraction solve pipeline confirmed working.

**Recommendation: Adopt** — for hull mesh wave load analysis in the Ship Plan CAD Pipeline (backlog 999.1).

---

## Installation Status

| Item | Value |
|---|---|
| Version | 2.3.1 |
| Location | `/mnt/local-analysis/capytaine-env` |
| Python | 3.12 |
| Install method | pip in dedicated venv |
| Pipeline test | PASS — radiation + diffraction solve on unit sphere |

Verified 2026-03-31: solver produces added mass, radiation damping, and excitation forces. Dataset assembly via `assemble_dataset()` returns clean xarray with `added_mass`, `radiation_damping`, `diffraction_force`, `Froude_Krylov_force`, `excitation_force`.

---

## Capabilities for Hull Hydrodynamics

### Core BEM Features

| Capability | Status | Notes |
|---|---|---|
| Added mass (frequency-dependent) | Yes | Full 6-DOF matrix |
| Radiation damping | Yes | Full 6-DOF matrix |
| Wave excitation forces (Froude-Krylov + diffraction) | Yes | Arbitrary wave headings |
| RAO computation | Yes | `capytaine.post_pro.rao` |
| Kochin functions (far-field patterns) | Yes | `capytaine.post_pro.kochin` |
| Impedance matrices | Yes | `capytaine.post_pro.impedance` |
| Free-surface elevation | Yes | `capytaine.post_pro.free_surfaces` |
| Multiple bodies | Yes | Via `CollectionOfMeshes` |
| Symmetry exploitation | Yes | Reflection, translational, axial — reduces solve time |

### Mesh Import — 25+ Formats

Confirmed supported extensions from `extension_dict`:

`dat`, `mar`, `nemoh`, `wamit`, `gdf`, `inp`, `hst`, `nat`, `msh` (Gmsh), `rad`, **`stl`**, `vtu`, `vtp`, `vtk`, `tec`, `med`, `vrml`, `wrl`, `nem`, `pnl`, `hams`

**Key for hull pipeline:** STL and Gmsh MSH are the two formats most likely produced by FreeCAD/Gmsh lofting in backlog 999.1. Both are natively supported — no format conversion step needed.

### Green Functions

| Green Function | Description |
|---|---|
| `Delhommeau` (default) | Classic Nemoh Green function, well-validated |
| `XieDelhommeau` | Variant with improved accuracy for certain cases |
| `HAMS_GF` | HAMS-compatible Green function |
| `FinGreen3D` | Finite-depth Green function |
| `LiangWuNoblesseGF` | Alternative formulation |

### Solver Engines

| Engine | Use Case |
|---|---|
| `BasicMatrixEngine` (default) | Direct LU decomposition, reliable for <5000 panels |
| `HierarchicalToeplitzMatrixEngine` | Fast for symmetric meshes |
| `HierarchicalPrecondMatrixEngine` | Large meshes with preconditioning |

---

## API Quality

**Excellent.** Clean, Pythonic API with sensible defaults.

Minimal working example (7 lines):
```python
import capytaine as cpt
body = cpt.FloatingBody(
    mesh=cpt.load_mesh("hull.stl"),
    dofs=cpt.rigid_body_dofs()
)
solver = cpt.BEMSolver()
result = solver.solve(cpt.RadiationProblem(body=body, radiating_dof="Heave", omega=1.0))
```

Key API strengths:
- `load_mesh()` auto-detects format from extension
- `rigid_body_dofs()` provides all 6 DOFs with one call
- `assemble_dataset()` produces xarray Dataset — integrates with pandas/matplotlib natively
- `export_dataset()` writes NetCDF for archival
- Logging via `cpt.set_logging("INFO")` — good debugging support

---

## Accuracy vs Commercial Solvers

Published benchmarks (EWTEC 2025 validation paper, NREL case studies):

- Capytaine results are **nearly identical to Nemoh** (shared algorithmic lineage)
- **Close to WAMIT** (industry gold standard) for single-body axisymmetric cases
- The direct method in recent Capytaine versions matches WAMIT/HAMS more closely for non-axisymmetric bodies and multiple wave headings
- Known gap: slightly less accurate than WAMIT for multi-body interaction at oblique headings — acceptable for single-hull analysis

For hull hydrodynamics (single body, multiple wave headings), Capytaine accuracy is sufficient for engineering design and classification screening.

---

## NREL Ecosystem Integration

| Tool | Relationship |
|---|---|
| **RAFT** | NREL's frequency-domain floating wind model; currently uses pyHAMS for BEM but Capytaine is a drop-in alternative |
| **WEIS** | Controls co-design framework; RAFT is the Level 1 dynamics model within WEIS |
| **WISDEM** | Wind plant optimization; feeds geometry to RAFT/WEIS |
| **OpenFAST** | Time-domain simulator; consumes HydroDyn coefficients that Capytaine can produce (via BEMRosetta .nc-to-WAMIT conversion or direct NetCDF) |
| **MoorPy** | Mooring analysis; complements Capytaine's hydrodynamic loads |
| **BEMRosetta** | Format converter/QA tool; reads Capytaine .nc output (see #1490 eval) |

Since April 2022, Capytaine development is funded by NREL/DOE — ensuring long-term alignment with the NREL floating offshore toolchain.

---

## Dependency Chain for Hull Analysis

```
999.1: Hull curve reconstruction (ship plans)
  → FreeCAD: 3D lofting from curves
    → Gmsh: Surface meshing (STL/MSH export)
      → Capytaine: BEM wave load analysis
        → Post-processing: RAO, added mass, damping plots
        → BEMRosetta (optional): format conversion, cross-solver QA
        → OpenFAST HydroDyn (optional): time-domain simulation
```

---

## Limitations

1. **Linear potential flow only** — no viscous effects, no wave breaking, no green water. Suitable for first-order wave loads; CFD (OpenFOAM) needed for extreme/nonlinear loads.
2. **Frequency domain only** — no direct time-domain stepping. Time-domain requires convolution of frequency-domain results (Cummins equation) or export to OpenFAST.
3. **No internal tank sloshing** — for ships with liquid cargo, sloshing must be handled separately.
4. **Mesh quality sensitivity** — BEM solvers are sensitive to mesh quality; irregular panels produce irregular frequencies. Mesh convergence study required for each hull.
5. **Performance** — `BasicMatrixEngine` scales as O(N^2) with panel count. Hulls over ~5000 panels should use hierarchical engines or symmetry exploitation.

---

## Recommendation

**Adopt** — Capytaine 2.3.1 is production-ready for hull mesh hydrodynamic analysis.

Rationale:
- Already installed and verified on dev-secondary
- Clean Python API, pip-installable, xarray-native output
- Reads STL/MSH directly from FreeCAD/Gmsh pipeline (no format conversion)
- NREL-funded, actively maintained, well-validated against WAMIT
- Covers the full BEM coefficient chain: added mass, damping, excitation, RAO
- Natural fit in the 999.1 dependency chain

### Next Steps

1. When 999.1 produces a hull mesh (STL/MSH), run Capytaine BEM analysis as first validation
2. Perform mesh convergence study on the hull geometry (vary panel count, check coefficient stability)
3. Compare against published hull hydrodynamic data or classification benchmarks
4. If OpenFAST time-domain is needed, evaluate BEMRosetta (#1490) for .nc-to-WAMIT conversion

---

## One-Liner Verdict

Capytaine is a validated, NREL-backed, pip-installable BEM solver with excellent Python API — adopt for hull wave load analysis as the natural next step after mesh generation in the Ship Plan CAD Pipeline.

---

## References

- [Capytaine documentation (v2.3.1)](https://capytaine.org/stable/)
- [Capytaine GitHub](https://github.com/capytaine/capytaine)
- [Capytaine paper (Ancellin & Dias)](https://www.researchgate.net/publication/332330798_Capytaine_a_Python-based_linear_potential_flow_solver)
- [EWTEC validation paper](https://publications.evolvingcities.org/proc-ewtec/article/view/725)
- [BEM solver comparison (case studies)](https://www.osti.gov/servlets/purl/2588370)
- [Nemoh vs WAMIT cargo ship comparison](https://cmst.curtin.edu.au/wp-content/uploads/sites/4/2017/07/Parisella-2016-Comparison-of-open-source-code-Nemoh-with-Wamit-for-cargo-ship-motions-in-shallow-water.pdf)
- [RAFT — NREL frequency-domain floating wind model](https://github.com/WISDEM/RAFT)
- [WEIS — Wind Energy with Integrated Servo-control](https://github.com/WISDEM/WEIS)
