# WRK-140 Plan: Integrate gmsh Meshing into digitalmodel Pipelines

## Objective
Wire gmsh meshing skill (WRK-139) into digitalmodel hydrodynamic analysis pipelines.

## Integration Points
1. GmshMeshBuilder Python module — GDF/DAT/MSH export from spec.yml geometry
2. AQWA runner — gmsh to DAT pre-processing
3. OrcaWave workflows — gmsh to GDF export
4. BEMRosetta pipeline — MSH v2.2 conversion

## Deliverables
- hydrodynamics/diffraction/gmsh_mesh_builder.py
- 26+ TDD tests
- Bug fixes in solvers/gmsh_meshing/
