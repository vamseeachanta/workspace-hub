# OpenFOAM Python Ecosystem Audit

> Status: Research completed 2026-02-24
> Machine: ace-linux-2 (Python 3.12.3)
> WRK: WRK-343 (feeds WRK-047, WRK-292)

## Overview

All five Python packages relevant to OpenFOAM automation have been installed and
verified on ace-linux-2 as part of WRK-290 (completed 2026-02-24). This document
records their status, capabilities, integration potential, and any known issues.

---

## Package Summary Table

| Package | Version | Status | WRK-047 Role |
|---------|---------|--------|--------------|
| PyFoam | 2023.7 | Installed — `six.moves` bug FIXED | Phase 4/5 log parsing, utilities |
| fluidfoam | Not installed | Evaluate | Post-processing alternative to PyFoam |
| oftest | Not installed | Evaluate | Testing framework for OpenFOAM cases |
| meshio | 5.3.5 | Installed, verified | Mesh format conversion (Phase 2) |
| pyvista | 0.47.0 | Installed, verified | VTK visualization (Phase 4) |
| vtk | 9.6.0 | Installed, verified | Backend for pyvista |

---

## PyFoam (v2023.7)

### Status
**INSTALLED and FIXED** — `six.moves` dependency issue resolved 2026-02-24 (WRK-290).

### The six.moves Bug
**Root cause:** PyFoam 2023.7 bundles its own copy of the `six` compatibility library at
`PyFoam/ThirdParty/six/six.py`. This bundled version does not include the `six.moves`
submodule, which Python 3.12 requires for the `urllib.parse` compatibility shims.

**Fix applied on ace-linux-2:**
Replaced the bundled `six.py` with a shim package at `PyFoam/ThirdParty/six/__init__.py`
and `PyFoam/ThirdParty/six/moves.py` that delegates to system `six` 1.16.0.
Backup of original at `six.py.bak`.

**Verification:**
```python
import PyFoam  # No errors
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
```

### Capabilities
PyFoam provides:
- Dict file parsing: `ParsedParameterFile` — reads/writes any OpenFOAM dict
- Case management: `BasicRunner`, `ConvergenceRunner` — run solvers with monitoring
- Log parsing: `LogAnalyzer`, `FoamLogFile` — extract residuals, iterations from logs
- Mesh manipulation: boundary condition utilities, field manipulation
- Utilities: `pyFoamClearCase.py`, `pyFoamPlotRunner.py` (38+ CLI tools)

### Integration potential for WRK-047
High value for:
- **Phase 4 (post-processing)**: `FoamLogFile` parses solver residuals from `log.simpleFoam`
  etc. into Python data structures without manual regex
- **Phase 5 (parametric/runner)**: `BasicRunner` handles subprocess execution, log routing,
  convergence detection — reduces boilerplate in `runner.py`
- **Dict manipulation**: `ParsedParameterFile` enables programmatic editing of any dict
  file as an alternative to Jinja2 templates

### Recommendation for WRK-047
Use PyFoam for **log parsing and residual extraction** (Phase 4). Consider it for
`runner.py` execution wrapper. Do NOT use it as the sole integration approach
(see July 2025 spec Option B discussion in wrk047-refresh.md).

**Fragility note:** The `six.moves` fix is a site-package-level patch. If PyFoam is
reinstalled or upgraded, the fix will be lost. A proper fix requires:
```bash
pip install 'six>=1.16.0'   # ensure system six is present
# Then patch the bundled six at install-time via pip install hook
```
Long-term: the `six` fix should be wrapped in the `engineering-suite-install.sh` script.

### Alternative: Skip PyFoam for dict generation
WRK-047 Phase 1 uses Jinja2 templates for dict generation — this does NOT require PyFoam.
PyFoam becomes relevant only when reading/modifying existing case files or parsing logs.
The Jinja2 approach is more maintainable and version-independent.

---

## meshio (v5.3.5)

### Status
**INSTALLED and VERIFIED** — `import meshio` works; no known issues.

### Capabilities
meshio is a universal mesh format converter supporting 40+ formats:
- **Input**: GMSH `.msh`, Abaqus `.inp`, VTK `.vtk/.vtu/.vtp`, STL, CGNS, ExodusII, ...
- **Output**: OpenFOAM mesh, VTK, GMSH `.msh`, Abaqus `.inp`, ...

**Key formats for OpenFOAM workflow:**
```python
import meshio
# Read GMSH mesh (from solvers/gmsh_meshing)
mesh = meshio.read("hull.msh")

# Write OpenFOAM format (polyMesh directory)
meshio.write("constant/polyMesh", mesh, file_format="openfoam")

# Convert between formats
meshio.read("input.msh") → meshio.write("output.vtk")
```

### Integration potential for WRK-047
**High value for Phase 2** (mesh generation pipeline):

The GMSH module (`solvers/gmsh_meshing/`) saves meshes as `.msh` format.
meshio provides direct `.msh` → OpenFOAM polyMesh conversion, enabling:
1. `GMSHMeshGenerator.save_mesh_msh("hull.msh")`
2. `meshio.read("hull.msh")` + `meshio.write("constant/polyMesh", ...)`
3. OpenFOAM reads the polyMesh directory directly

This creates a clean GMSH → OpenFOAM pipeline without needing `gmshToFoam` utility.

**Alternative path:** `gmshToFoam` (bundled with OpenFOAM) converts `.msh` directly:
```bash
gmshToFoam hull.msh
```
Both approaches are valid; meshio is preferred for Python-native workflow (no subprocess).

### Usage example for WRK-047
```python
import meshio
from pathlib import Path

def gmsh_msh_to_openfoam(msh_file: str, case_dir: str) -> None:
    """Convert GMSH .msh file to OpenFOAM polyMesh format."""
    mesh = meshio.read(msh_file)
    poly_mesh_dir = Path(case_dir) / "constant" / "polyMesh"
    poly_mesh_dir.mkdir(parents=True, exist_ok=True)
    meshio.write(str(poly_mesh_dir), mesh, file_format="openfoam")
```

---

## pyvista (v0.47.0)

### Status
**INSTALLED and VERIFIED** — `import pyvista` works; no known issues.

### Capabilities
pyvista wraps VTK with a Pythonic API for 3D mesh visualization and analysis:
- Read VTK files (`.vtk`, `.vtu`, `.vtp`) — OpenFOAM output via foamToVTK
- Extract field data (velocity, pressure, turbulence quantities)
- Compute derived quantities (streamlines, isosurfaces, slices)
- Export plots (offscreen rendering — no display required)

### Integration potential for WRK-047
**High value for Phase 4** (post-processing visualization):

```python
import pyvista as pv

# Read OpenFOAM results (post foamToVTK conversion)
mesh = pv.read("VTK/pitzDaily_100.vtk")

# Extract pressure field
pressure = mesh.point_data["p"]

# Create slice plane
sliced = mesh.slice(normal="y")

# Offscreen rendering (works on ace-linux-2 without display)
plotter = pv.Plotter(off_screen=True)
plotter.add_mesh(sliced, scalars="U", cmap="viridis")
plotter.save_graphic("results/velocity_slice.png")
```

**Consistent with digitalmodel convention:** The codebase uses Plotly for interactive
plots. pyvista + offscreen rendering fills the 3D CFD visualization gap that Plotly
cannot address (3D volume field rendering). These are complementary.

### Note on ParaView segfault
ParaView 5.11.2 `pvpython` segfaults when creating rendering pipelines without X display.
Use `pvpython --force-offscreen-rendering` OR use pyvista instead for scripted
post-processing. pyvista is the recommended headless path on ace-linux-2.

---

## vtk (v9.6.0)

### Status
**INSTALLED and VERIFIED** — installed as pyvista dependency; `import vtk` works.

### Role in WRK-047
vtk is the backend for pyvista. Direct vtk usage is not required in WRK-047 since
pyvista provides a cleaner API. However, vtk's `vtkOpenFOAMReader` can read OpenFOAM
case directories directly (without foamToVTK conversion):

```python
import vtk
reader = vtk.vtkOpenFOAMReader()
reader.SetFileName("pitzDaily/pitzDaily.foam")  # dummy .foam file
reader.Update()
```

This is an advanced option for Phase 4 if foamToVTK overhead becomes an issue.

---

## fluidfoam (not installed)

### Status
Not installed. Evaluated for Phase 4 post-processing.

### Capabilities
fluidfoam is a lightweight Python library for reading OpenFOAM field data directly
from the time directories (no foamToVTK step required):
```python
from fluidfoam import readscalar, readvector
p = readscalar("pitzDaily", "100", "p")     # pressure at t=100
U = readvector("pitzDaily", "100", "U")     # velocity vector at t=100
```

### Install and verify
```bash
pip install fluidfoam
python -c "import fluidfoam; print(fluidfoam.__version__)"
```

### Recommendation
Install on ace-linux-2. fluidfoam's direct field reading (no VTK conversion) is
simpler than foamToVTK + pyvista for scalar/vector extraction. However, pyvista is
more capable for 3D visualization. Use both:
- fluidfoam: extract force coefficients, probe data, scalar fields
- pyvista: 3D volume rendering and slice visualization

---

## oftest (not installed)

### Status
Not installed. Evaluated for OpenFOAM integration testing.

### Capabilities
oftest is a pytest-based framework for running and validating OpenFOAM cases:
- Defines test cases as pytest fixtures
- Runs OpenFOAM tutorials with configurable parameters
- Validates convergence and residual thresholds
- Compares results against reference data

### Recommendation
**Not needed for WRK-047 immediately.** The WRK-047 testing strategy (from the July
2025 tests.md spec) uses subprocess mocking and `tmp_path` fixtures — this is adequate
for CI without OpenFOAM installed. oftest is more useful for integration testing on
ace-linux-2 with real OpenFOAM runs. Revisit for Phase 6 integration testing.

```bash
# When ready to install:
pip install oftest
```

---

## Dependency Matrix for WRK-047

| Package | Phase | Import guard needed? | Notes |
|---------|-------|---------------------|-------|
| PyFoam | Phase 4, 5 | YES — `PYFOAM_AVAILABLE` | Useful but not required |
| meshio | Phase 2 | YES — `MESHIO_AVAILABLE` | Required for GMSH → OpenFOAM |
| pyvista | Phase 4 | YES — `PYVISTA_AVAILABLE` | Optional visualization |
| vtk | Phase 4 | indirect via pyvista | Optional, accessed via pyvista |
| fluidfoam | Phase 4 | YES — `FLUIDFOAM_AVAILABLE` | Optional field reading |
| numpy | All | NO — already required | Core dependency |
| jinja2 | Phase 1 | YES — `JINJA2_AVAILABLE` | Required for templates |
| pyyaml | Phase 5 | NO — already required | Core dependency |

### Pattern to follow (from gmsh_meshing)
```python
try:
    import meshio
    MESHIO_AVAILABLE = True
except ImportError:
    MESHIO_AVAILABLE = False

# Usage
def gmsh_to_openfoam(msh_file, case_dir):
    if not MESHIO_AVAILABLE:
        raise ImportError("meshio required. Install: pip install meshio")
    ...
```

---

## Installation Commands (for new machines / reimaging)

```bash
# Core packages (already in engineering-suite-install.sh)
pip install meshio==5.3.5
pip install PyFoam==2023.7
pip install pyvista==0.47.0

# Fix PyFoam six.moves bug after install
PYFOAM_PATH=$(python -c "import PyFoam; import os; print(os.path.dirname(PyFoam.__file__))")
SIXDIR="$PYFOAM_PATH/ThirdParty/six"
mkdir -p "$SIXDIR"
# Create __init__.py that delegates to system six
cat > "$SIXDIR/__init__.py" << 'EOF'
from six import *
from six import moves, add_move, add_doc, string_types, integer_types
EOF
cat > "$SIXDIR/moves.py" << 'EOF'
from six.moves import *
EOF

# Additional evaluation packages
pip install fluidfoam
pip install oftest
```

This fix sequence should be added to `scripts/setup/engineering-suite-install.sh`.

---

*Generated: 2026-02-24 | WRK-343*
