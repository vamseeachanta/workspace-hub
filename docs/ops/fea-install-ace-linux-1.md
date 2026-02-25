# FEA Installation on ace-linux-1 (WRK-291)

**Date:** 2026-02-24
**Machine:** ace-linux-1 (Ubuntu 24.04.4 LTS)
**User:** vamsee (sudo requires password — user-space install only)
**Source:** WRK-289 research (top 3 FEA recommendations)

---

## Programs Installed

| Program | Version | Method | Location | Status |
|---------|---------|--------|----------|--------|
| **CalculiX CCX** | 2.21 | .deb extracted (no root) | `~/.local/bin/ccx` | Installed + verified |
| **CalculiX CGX** | 2.21 | .deb extracted (no root) | `~/.local/bin/cgx` | Installed (GUI requires X) |
| **Elmer FEM** | 26.1 (2026-02-24) | Built from source with miniforge3 compilers | `~/.local/elmer/` | Installed + verified |
| **FEniCSx** | 0.10.0 | conda-forge via miniforge3 | `~/miniforge3/envs/fenicsx-env` | Installed + verified |
| **Gmsh** | 4.15.1 | pip (bundled binary + Python API) | `~/.local/bin/gmsh` | Installed + verified |
| **Miniforge3** | conda 26.1.0 | user-space installer | `~/miniforge3/` | Installed (used by FEniCSx + Elmer build) |
| **ccx2paraview** | 3.2.0 | pip | `~/.local/bin/ccx2paraview` | Installed |
| **pycalculix** | 1.1.4 | pip | `~/.local/lib/python3.12/` | Installed |
| **meshio** | 5.3.5 | pip | `~/.local/lib/python3.12/` | Installed |
| **pyvista** | 0.47.1 | pip | `~/.local/lib/python3.12/` | Installed |

---

## Wrapper Scripts

All wrappers are in `~/.local/bin/` (already on PATH via .bashrc):

- `ccx` — sets `LD_LIBRARY_PATH=~/.local/lib/fea-libs` and calls `ccx_2.21`
- `cgx` — same LD_LIBRARY_PATH pattern (GUI, needs X display)
- `ElmerSolver` — sets `LD_LIBRARY_PATH=~/miniforge3/lib`, calls `~/.local/elmer/bin/ElmerSolver`
- `ElmerGrid` — same pattern, calls `~/.local/elmer/bin/ElmerGrid`
- `fenicsx-python` — calls `~/miniforge3/envs/fenicsx-env/bin/python3`

---

## Environment Variables (.bashrc)

```bash
# FEA Tools (WRK-291)
export ELMER_HOME="$HOME/.local/elmer"
export ELMER_LIB="$HOME/.local/elmer/lib/elmersolver"
export PATH="$HOME/miniforge3/bin:$PATH"
```

---

## Shared Libraries (CalculiX user-space deps)

Downloaded and extracted to `~/.local/lib/fea-libs/`:
- `libspooles.so.2.2` (from libspooles2.2t64)
- `libarpack.so.2` (from libarpack2t64)
- `libmpi.so.40` (from libopenmpi3t64)
- `libopen-rte.so.40`, `libopen-pal.so.40` (from libopenmpi3t64)
- `libhwloc.so.15` (from libhwloc15)
- `libevent_core-2.1.so.7`, `libevent_pthreads-2.1.so.7`
- `libglut.so.3.12` (CGX only, from libglut3.12)
- `libSNL.so.0` (CGX only, from libsnl0t64)

Raw .deb packages stored in:
`scripts/setup/fea-pkgs/*.deb`

---

## Smoke Tests

### CalculiX — Cantilever Beam (Static Structural)

```bash
ccx /tmp/fea-smoketest/cantilever/beam
```

Result: Max tip deflection Uy = -0.177 mm (theoretical 0.190 mm for 2-element mesh).
Output converted to VTK via `ccx2paraview beam.frd vtk`.

### Elmer FEM — Heat Conduction

```bash
ElmerGrid 14 2 heat_plate.msh
ElmerSolver heat.sif
```

Result: Temperature range 293.15–373.15 K (linear gradient, correct boundary values).

### FEniCSx — Heat Conduction

```bash
fenicsx-python /tmp/fea-smoketest/fenicsx/heat_test.py
```

Result: Temperature range 293.15–373.15 K, mean 333.15 K. PASS.

### Gmsh — Mesh Generation

```python
import gmsh  # version 4.15.1
gmsh.model.occ.addBox(0, 0, 0, 100, 10, 10)
gmsh.model.mesh.generate(3)
```

Result: 190 nodes, 433 3D elements for 100x10x10mm box. PASS.

---

## Known Issues

| Issue | Details | Workaround |
|-------|---------|------------|
| CalculiX apt version is 2.21 | Ubuntu 24.04 repos have v2.21, not v2.23 | Use conda-forge when root available: `conda install -c conda-forge calculix` |
| CGX requires X display | CalculiX pre/post-processor is GUI only | Use FreeCAD FEM workbench or command-line workflow instead |
| Elmer PPA requires root | `ppa:elmer-csc-ubuntu/elmer-csc-ppa` not addable without sudo | Built from source using miniforge3 compilers (v26.1, current dev) |
| FEniCSx not on PyPI | `fenics-dolfinx` not available via pip | conda-forge via miniforge3 |
| FEniCSx API change in 0.10.0 | `LinearProblem` now requires `petsc_options_prefix` kwarg | Add `petsc_options_prefix="..."` to all LinearProblem calls |
| Elmer build time | Full source build takes ~5 min on 32-core machine | Pre-built binary available when PPA accessible (with root) |

---

## Integration Summary

| FEA Tool | Gmsh | ParaView | FreeCAD |
|----------|------|----------|---------|
| CalculiX | Export to .inp format | Via ccx2paraview (VTK) | Native FEM workbench |
| Elmer FEM | ElmerGrid 14 2 file.msh | Native VTU output | FEM workbench (1.0+) |
| FEniCSx | Python: dolfinx.io.gmshio | XDMF output or pyvista | Export/import only |

---

## Quick Start Cheatsheet

```bash
# CalculiX structural analysis
ccx problem_name          # solve (reads problem_name.inp)
python3 -m ccx2paraview problem_name.frd vtk  # convert to VTK

# Elmer FEM heat transfer
ElmerGrid 14 2 mesh.msh   # convert Gmsh mesh to Elmer format
ElmerSolver problem.sif   # solve

# FEniCSx custom FEA
fenicsx-python solve.py   # run FEniCSx Python script

# Gmsh mesh generation
python3 -c "import gmsh; ..."  # Python API
```

---

*Installed 2026-02-24 from WRK-291. Reference: `docs/research/open-source-fea-survey.md`*
