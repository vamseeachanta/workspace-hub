---
name: aqwa-input
description: AQWA input file formats (LIS, DAT, MES), analysis type configurations,
  standalone DAT conventions, mesh quality rules, and complete workflow config examples.
type: reference
version: 1.0.0
updated: 2026-03-16
category: engineering
triggers:
- AQWA input file
- AQWA DAT file
- AQWA MES file
- AQWA mesh quality
- AQWA configuration
- AQWA workflow config
capabilities: []
requires: []
see_also:
- aqwa-analysis
tags: []
scripts_exempt: true
---
# AQWA Input Skill

Input file formats, analysis configurations, DAT file conventions, and mesh quality for ANSYS AQWA. See [aqwa](../SKILL.md) for Python API.

## File Format Support

### LIS Files (Listing Output)

Primary output containing RAOs (amplitude/phase), added mass matrices, damping matrices, wave excitation forces, drift forces.

### DAT Files (Data Input)

Input containing hull geometry, mass properties, analysis settings, wave conditions.

### MES Files (Mesh)

Mesh definition: panel geometry, node coordinates, panel connectivity.

## Analysis Type Configurations

### RAO Extraction

```yaml
aqwa_analysis:
  rao_extraction:
    flag: true
    input_file: "aqwa_results/vessel.LIS"
    vessel_name: "FPSO"
    wave_directions: [0, 45, 90, 135, 180]
    output:
      rao_file: "results/vessel_raos.csv"
      plot_file: "results/rao_plots.html"
      format: "amplitude_phase"  # or real_imaginary
```

### Hydrodynamic Coefficients

```yaml
aqwa_analysis:
  coefficients:
    flag: true
    input_file: "aqwa_results/vessel.LIS"
    frequencies: "all"  # or specific list [0.1, 0.2, 0.3]
    output:
      added_mass_file: "results/added_mass.csv"
      damping_file: "results/damping.csv"
      matrices_file: "results/hydro_matrices.json"
```

### File Processing

```yaml
aqwa_analysis:
  file_processing:
    flag: true
    files:
      - path: "aqwa_results/vessel.LIS"
        type: "lis"
      - path: "aqwa_results/vessel.DAT"
        type: "dat"
    extract: ["raos", "added_mass", "damping", "wave_forces", "drift_forces"]
    output_directory: "results/aqwa_processed/"
```

### Viscous Damping

```yaml
aqwa_analysis:
  viscous_damping:
    flag: true
    method: "empirical"  # or decay_test
    vessel: { length: 300.0, beam: 50.0, draft: 20.0 }
    motions: ["roll", "pitch", "heave"]
    empirical_factors: { roll_percentage: 5.0, pitch_percentage: 3.0, heave_percentage: 2.0 }
    output:
      damping_file: "results/viscous_damping.json"
```

## Standalone DAT File Format (Non-Workbench)

Critical conventions for standalone `.DAT` input files:

```
Element type:     QPPL DIFF    (NOT just QPPL — without DIFF, elements are "NON-DIFFRACTING")
ILID card:        1ILID AUTO 21  (after ZLWL — required for irregular frequency removal)
SEAG card:        SEAG (nx, ny)  (2 params only in non-Workbench mode, NOT 6-param bounding box)
OPTIONS GOON:     Continue past non-fatal errors (separate line, before feature OPTIONS)
Line length:      Max 80 columns per line (AQWA enforces strict column limits)
```

## Mesh Quality Rules (FATAL)

- Panels must be roughly square (aspect ratio near 1:1)
- "Facet Radius" distance check at 90-degree corners of box geometries
- For a 100m x 20m x 8m barge: minimum nx=40, ny=8, nz=4 (704 panels)
- `OPTIONS GOON` does NOT bypass FATAL mesh quality errors

```python
from digitalmodel.aqwa.mesh_check import AqwaMeshCheck

mesh = AqwaMeshCheck()
mesh.load("geometry/hull.mes")
quality = mesh.check_quality()

if quality["min_aspect_ratio"] < 0.1:
    print("Warning: Poor aspect ratio panels detected")
if quality["intersecting_panels"] > 0:
    print(f"Error: {quality['intersecting_panels']} intersecting panels")
```

## Complete Workflow Config

```yaml
basename: aqwa_analysis

aqwa_analysis:
  file_processing:
    flag: true
    input_file: "aqwa_results/fpso.LIS"
    output_directory: "results/"
  rao_extraction:
    flag: true
    wave_directions: [0, 30, 60, 90, 120, 150, 180]
    output:
      rao_file: "results/fpso_raos.csv"
      orcaflex_file: "results/fpso_raos.yml"
      plots: "results/rao_plots.html"
  coefficients:
    flag: true
    output: { added_mass: "results/added_mass.csv", damping: "results/damping.csv" }
  viscous_damping:
    flag: true
    method: "percentage_critical"
    values: { roll: 5.0, pitch: 3.0, heave: 2.0 }
  validation:
    flag: true
    checks: [symmetry, low_frequency, kramers_kronig]
    output: { report: "results/validation_report.json" }
```

## Best Practices

1. **Frequency range** — ensure frequencies cover wave spectrum of interest
2. **Direction resolution** — use 30-degree or finer for asymmetric vessels
3. **Panel density** — verify mesh convergence for accurate results
4. **Low frequency** — check added mass at low frequencies for stability
5. **Viscous damping** — always add viscous damping for roll motion

## Related Skills

- [aqwa](../SKILL.md) — Hub skill with Python API
- [aqwa/output](../output/SKILL.md) — Output formats and validation
- [aqwa/reference](../reference/SKILL.md) — Solver stages and OPTIONS keywords
