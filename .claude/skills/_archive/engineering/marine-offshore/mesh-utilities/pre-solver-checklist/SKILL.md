---
name: mesh-utilities-pre-solver-checklist
description: 'Sub-skill of mesh-utilities: Pre-Solver Checklist.'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Pre-Solver Checklist

## Pre-Solver Checklist


Before running AQWA, OrcaWave, or BEMRosetta, verify:

```python
def pre_solver_checklist(mesh_path: str, solver: str) -> bool:
    """Run pre-solver validation checklist.

    Args:
        mesh_path: Path to mesh file
        solver: Target solver name

    Returns:
        True if mesh passes all checks
    """
    from digitalmodel.hydrodynamics.bemrosetta.mesh import BaseMeshHandler
    from digitalmodel.hydrodynamics.diffraction.geometry_quality import (
        GeometryQualityChecker,
    )

    handler = BaseMeshHandler()
    mesh = handler.read(mesh_path)

    checker = GeometryQualityChecker()
    report = checker.generate_report(mesh_path)

    checks = {

*See sub-skills for full details.*
