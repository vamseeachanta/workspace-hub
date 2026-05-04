---
name: yaml-configuration-example-1-orcaflex-mooring-configuration
description: 'Sub-skill of yaml-configuration: Example 1: OrcaFlex Mooring Configuration
  (+5).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Example 1: OrcaFlex Mooring Configuration (+5)

## Example 1: OrcaFlex Mooring Configuration


```yaml
# config/mooring_analysis.yaml
---
metadata:
  analysis_name: "FPSO Mooring System"
  analysis_type: "dynamic_mooring"
  created: "2026-01-06"
  author: "Marine Engineering Team"
  version: 1.0


*See sub-skills for full details.*

## Example 2: Hydrodynamic Analysis Configuration


```yaml
# config/hydrodynamic_analysis.yaml
---
analysis:
  type: "frequency_domain"
  software: "AQWA"  # or "WAMIT", "OrcaWave"

geometry:
  input_file: "../models/vessel_geometry.gdf"
  mesh:

*See sub-skills for full details.*

## Example 3: Fatigue Analysis Configuration


```yaml
# config/fatigue_analysis.yaml
---
analysis:
  name: "Mooring Line Fatigue Assessment"
  type: "spectral_fatigue"
  standard: "DNV-RP-C203"

input_data:
  tension_rao:

*See sub-skills for full details.*

## Example 4: Multi-Analysis Workflow


```yaml
# config/workflow_config.yaml
---
workflow:
  name: "Complete Mooring Analysis Workflow"
  version: 1.0

stages:
  - stage: 1
    name: "Hydrodynamic Analysis"

*See sub-skills for full details.*

## Example 5: Vessel Library


```yaml
# config/vessel_library.yaml
---
# Vessel templates library

vessels:
  fpso_standard: &fpso
    type: "FPSO"
    dimensions:
      length: 320

*See sub-skills for full details.*

## Example 6: Parameter Variations


```yaml
# config/parametric_study.yaml
---
parametric_study:
  name: "Mooring Pretension Sensitivity"
  base_config: "../config/mooring_analysis.yaml"

  parameters:
    - name: "pretension"
      type: "linear"

*See sub-skills for full details.*
