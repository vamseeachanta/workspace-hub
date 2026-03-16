---
name: diffraction-analysis-unit-conversion-traps
description: 'Sub-skill of diffraction-analysis: Unit Conversion Traps (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Unit Conversion Traps (+3)

## Unit Conversion Traps


| Source | Mass Unit | Inertia Unit | Density | Convert to spec.yml |
|--------|-----------|-------------|---------|---------------------|
| WAMIT `.frc` | te | te·m² | 1 (te/m³) | ×1000 for kg, kg·m² |
| OrcaWave | te | te·m² | 1 (te/m³) | ×1000 for kg, kg·m² |
| AQWA | kg | kg·m² | 1025 (kg/m³) | Direct |
| spec.yml | kg | kg·m² | kg/m³ | — |

**Trap**: When porting from WAMIT `.frc` to spec.yml, multiply inertia by 1000 (te·m² → kg·m²). Do NOT multiply twice — the ISSC TLP case 2.5 had a 1000x error from double conversion.

## Phase Correlation for Zero-Magnitude DOFs


Fixed DOFs (e.g. heave/roll/pitch on TLPs) produce zero RAO magnitudes. Phase is undefined (`atan2(0,0)` noise), so:
- `multi_solver_comparator.py`: overrides phase correlation to 1.0 when `peak_mag < 1e-10`
- `validate_owd_vs_spec.py`: skips DOFs with `max_diff < 1e-6` in pass/fail verdict

## Benchmark Report Geometry Schematics


The `build_mesh_schematic_html()` in `benchmark_plotter.py` renders interactive 3D Plotly mesh visualizations. It requires `mesh_path` in `solver_metadata`. When using `build_orcawave_metadata_from_yml()`, propagate `mesh_path` from `build_solver_metadata()` base metadata — the enriched YAML metadata doesn't resolve mesh paths.

## Mesh Quality Assessment


- **Adjacent panel ratio** (between neighbors) is the key metric — not global min/max area ratio
- Gradual size variation is acceptable even with large global ratio
- Report uses `NOTE:` prefix (informational) not `WARNING:` for area ratio
- Advanced metrics (Jacobian, aspect ratio, skewness) available via gmsh meshing tool
