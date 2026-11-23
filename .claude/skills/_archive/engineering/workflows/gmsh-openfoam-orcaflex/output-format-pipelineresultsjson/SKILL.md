---
name: gmsh-openfoam-orcaflex-output-format-pipelineresultsjson
description: 'Sub-skill of gmsh-openfoam-orcaflex: Output Format: pipeline_results.json.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Output Format: pipeline_results.json

## Output Format: pipeline_results.json


```json
{
  "version": "1.0.0",
  "parameters": {"diameter_m": 1.0, "length_m": 5.0, "velocity_m_s": 1.5},
  "passed": true,
  "stages": {
    "gmsh":                {"passed": true, "cell_count": 980, ...},
    "gate1_mesh_quality":  {"passed": true, "max_skewness": 0.4, ...},
    "convert_gmsh_to_foam":{"passed": true, "method": "gmshToFoam", ...},
    "openfoam":            {"passed": true, "drag_force_N": 5765.6, ...},
    "gate2_cfd_convergence":{"passed": true, "converged": true, ...},
    "convert_foam_to_orcaflex":{"passed": true, "row_count": 50, ...},
    "orcaflex":            {"passed": true, "max_deflection_m": 0.002, ...}
  },
  "summary": {
    "drag_force_N": 5765.62,
    "max_deflection_m": 0.002,
    "max_tension_N": 6210.5,
    "mesh_cells": 980,
    "stub_mode": true
  }
}
```
