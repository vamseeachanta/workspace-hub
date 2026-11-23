---
name: hydrodynamic-analysis-wamit-workflow
description: 'Sub-skill of hydrodynamic-analysis: WAMIT Workflow (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# WAMIT Workflow (+1)

## WAMIT Workflow


```yaml
wamit_workflow:
  step_1_geometry:
    tool: "Rhino, GHS, or MultiSurf"
    output: "geometry.gdf"
    requirements:
      - "Waterline at z=0"
      - "Wetted surface only"
      - "Right-hand coordinate system"

  step_2_panel_mesh:
    tool: "WAMIT-PGEN or Multisurf"
    output: "vessel.gdf"
    quality_checks:
      - "Panel aspect ratio < 3:1"
      - "Panel size < λ/6"
      - "Use symmetry if applicable"

  step_3_run_wamit:
    input_files:
      - "vessel.frc"  # Force control
      - "vessel.pot"  # Potential control
      - "vessel.gdf"  # Geometry
    output_files:
      - "vessel.out"  # Main output
      - "vessel.1"    # Added mass/damping
      - "vessel.3"    # Wave excitation

  step_4_post_processing:
    tools:
      - "WAMIT-VIEW"
      - "Python (read .1, .3 files)"
      - "OrcaFlex (import RAOs)"
```


## AQWA Workflow


```yaml
aqwa_workflow:
  step_1_geometry:
    tool: "ANSYS DesignModeler or SpaceClaim"
    output: "geometry.scdoc"

  step_2_mesh:
    tool: "AQWA-GS (meshing)"
    output: "vessel.anl"
    settings:
      element_size: "Auto or manual"
      symmetry: "Use if applicable"

  step_3_analysis:
    solver: "AQWA-NAUT or AQWA-LINE"
    analysis_types:
      - "Hydrodynamic diffraction"
      - "Response calculation"

  step_4_results:
    output: "vessel.LIS"
    exports:
      - "RAOs → CSV"
      - "Added mass/damping → CSV"
      - "OrcaFlex YML"
```
