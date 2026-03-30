---
name: freecad-automation-core-capabilities
description: 'Sub-skill of freecad-automation: Core Capabilities (+4).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Core Capabilities (+4)

## Core Capabilities


- **CAD Automation**: Script-based FreeCAD operations
- **Batch Processing**: Parallel file processing with pattern matching
- **Parametric Design**: Design tables and parameter variations
- **Assembly Management**: Constraint solving and assembly creation
- **FEM Preprocessing**: Mesh generation and boundary conditions
- **Drawing Generation**: Automatic dimensioning and views
- **Natural Language Processing**: Convert commands to CAD operations
- **Script Generation**: Auto-generate Python scripts from prompts

## Marine Engineering Specialization


- Hull NURBS generation from HullProfile stations (scipy fallback without FreeCAD)
- Hydrostatic analysis: displaced volume, waterplane area, KB, BM via section integration
- Stability calculations
- Mooring system configuration
- Structural analysis preprocessing

## FEM Analysis (v2.0)


- CalculiX INP file generation from gmsh mesh data
- FRD/DAT result parsing (displacements, von Mises stress)
- End-to-end FEM chain: geometry → mesh → solve → extract
- Plate-with-hole Kt validation (Kt ≈ 3.0)

## Design Table Studies (v2.0)


- YAML-driven parametric sweeps (cartesian product of parameters)
- Process-level parallelism via multiprocessing (FreeCAD not thread-safe)
- Comparison YAML output for all variations
- Manifold validation: watertight check, self-intersection, normal consistency

## Integration Points


- **OrcaFlex**: Data exchange for hydrodynamic analysis
- **AQWA**: Diffraction analysis geometry
- **Signal Analysis**: Module connectivity
- **REST API**: External system integration
