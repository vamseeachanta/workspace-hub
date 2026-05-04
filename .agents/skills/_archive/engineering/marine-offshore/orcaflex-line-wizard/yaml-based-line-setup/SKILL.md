---
name: orcaflex-line-wizard-yaml-based-line-setup
description: 'Sub-skill of orcaflex-line-wizard: YAML-Based Line Setup (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# YAML-Based Line Setup (+1)

## YAML-Based Line Setup


```yaml
# configs/line_setup.yml

line_setup:
  calculation_mode: "Calculate line lengths"
  max_damping: 50

  lines:
    - name: "Mooring_Leg_1"
      target_variable: "Tension"

*See sub-skills for full details.*

## Multi-Segment Line Configuration


```yaml
# configs/line_sections.yml

lines:
  - name: "Catenary_Mooring_1"
    sections:
      - line_type: "Chain_R4_84mm"
        length: 80.0
        segment_length: 4.0


*See sub-skills for full details.*
