---
name: freecad-automation-fem-chain-workflow
description: 'Sub-skill of freecad-automation: CalculiX FEM analysis chain — geometry creation via gmsh, INP export, ccx solve, and result extraction.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# FEM Chain Workflow (CalculiX)

## Overview

End-to-end structural FEM pipeline: gmsh geometry → INP file → CalculiX solve → stress/displacement extraction.

## Pipeline Steps

1. **Create geometry** — gmsh OCC kernel (plate-with-hole, STEP import, etc.)
2. **Define analysis** — material, BCs, loads → INP file via INPWriter
3. **Solve** — CalculiX `ccx` subprocess
4. **Extract results** — parse `.frd` (nodal fields) and `.dat` (reactions)

## Quick Start: Plate-with-Hole Validation

```python
from digitalmodel.solvers.calculix.fem_chain import FEMChain

chain = FEMChain()
result = chain.run_plate_validation(sigma_applied=100.0)
print(f"Kt = {result['kt']:.3f}")  # ~3.0 within 5%
```

## Custom Analysis

```python
from pathlib import Path
from digitalmodel.solvers.calculix.fem_chain import FEMChain

chain = FEMChain(work_dir=Path("/tmp/my_fem"))

# 1. Create geometry (quarter-symmetry plate with hole)
stats = chain.create_plate_with_hole(
    plate_w=200.0, plate_h=200.0, hole_r=10.0,
    thickness=1.0, element_size=5.0,
)

# 2. Setup analysis
chain.setup_analysis(
    material={"name": "STEEL", "E": 210000.0, "nu": 0.3},
    loads=[{
        "type": "cload", "node_set": "LOAD",
        "dof": 1, "magnitude": 100.0, "direction": (1, 0, 0),
    }],
    boundary_conditions=[
        {"node_set": "SYM_X", "dof_start": 1, "dof_end": 1},
        {"node_set": "SYM_Y", "dof_start": 2, "dof_end": 2},
        {"node_set": "FIX_Z", "dof_start": 3, "dof_end": 3},
    ],
)

# 3. Solve
status = chain.solve()
assert status["success"]

# 4. Results
results = chain.extract_results()
print(f"Max von Mises: {results['max_von_mises']:.1f} MPa")
print(f"Max displacement: {results['max_displacement']:.6f} mm")
```

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `FEMChain` | `solvers.calculix.fem_chain` | End-to-end orchestrator |
| `INPWriter` | `solvers.calculix.inp_writer` | Mesh → INP file conversion |
| `CalculiXResultParser` | `solvers.calculix.result_parser` | `.frd`/`.dat` parsing |
| `GMSHMeshGenerator` | `solvers.gmsh_meshing.mesh_generator` | STEP import + meshing |

## Prerequisites

- `gmsh` Python package (pip install gmsh)
- `ccx` binary on PATH (CalculiX solver)
- Check availability: `from digitalmodel.solvers.calculix.fem_chain import is_calculix_available`

## Node Sets (Plate-with-Hole)

| Set | Description |
|-----|-------------|
| `SYM_X` | Nodes on x=0 symmetry plane |
| `SYM_Y` | Nodes on y=0 symmetry plane |
| `FIX_Z` | Nodes on z=0 face (out-of-plane constraint) |
| `LOAD` | Nodes on far edge (x=W/2) for applied traction |

## Validated Results

- Plate-with-hole Kt within 5% of theoretical 3.0 (d/W < 0.3)
- Quarter-symmetry model with W/d > 5
