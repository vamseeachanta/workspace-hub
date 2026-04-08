---
title: "BEMRosetta Tool"
tags: [bemrosetta, mesh-conversion, nemoh, hydrodynamics]
sources:
  - dark-intelligence-extractions
added: 2026-04-08
last_updated: 2026-04-08
---

# BEMRosetta Tool

BEMRosetta is a CLI mesh conversion and hydrodynamic data processing tool used in the workspace-hub ecosystem to translate between mesh formats required by different hydrodynamic solvers (OrcaFlex/OrcaWave, AQWA, WAMIT, Nemoh).

## Executable and Invocation

```
$BEMROSETTA_HOME/BEMRosetta_cl.exe
```

The `_cl` suffix denotes the command-line variant (as opposed to the GUI version).

## Primary Mode: Mesh Conversion

BEMRosetta is invoked in `-mesh` mode for converting between panel mesh formats:

```bash
BEMRosetta_cl.exe -mesh input_file.gdf -o output_file.dat -fmt aqwa
```

### Supported Formats

| Format | Solver | Extension |
|--------|--------|-----------|
| GDF | WAMIT | `.gdf` |
| DAT | AQWA | `.dat` |
| Nemoh | Nemoh | `.dat` (different structure) |
| STL | General | `.stl` |
| OrcaWave | OrcaWave | `.owr` |

## Nemoh Integration

Nemoh is the open-source BEM (Boundary Element Method) hydrodynamic solver that BEMRosetta wraps and supports natively. BEMRosetta can:

- Convert meshes into Nemoh-compatible format
- Read Nemoh output for post-processing
- Translate Nemoh results into formats consumable by commercial solvers

## Typical Workflow

1. Generate or obtain hull mesh in one format (e.g., GDF from WAMIT)
2. Run BEMRosetta to convert to target solver format (e.g., AQWA DAT)
3. Verify converted mesh: panel count, normals, watertightness
4. Feed converted mesh into target solver input file

## Cross-References

- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
