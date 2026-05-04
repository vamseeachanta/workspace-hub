---
name: mooring-design-yaml-configuration
description: 'Sub-skill of mooring-design: YAML Configuration.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# YAML Configuration

## YAML Configuration


```yaml
# config/mooring_design.yaml

system:
  type: calm
  water_depth: 100.0
  design_life_years: 20

vessel:
  type: tanker
  length: 280.0
  beam: 46.0
  draft: 17.5
  windage_area: 6000.0

mooring_pattern:
  n_lines: 6
  anchor_radius: 450.0
  first_line_heading: 30.0  # degrees

line_configuration:
  segments:
    - type: chain
      length: 400.0
      diameter: 84.0

*See sub-skills for full details.*
