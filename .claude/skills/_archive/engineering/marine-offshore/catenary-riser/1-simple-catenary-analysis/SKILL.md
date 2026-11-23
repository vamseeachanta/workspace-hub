---
name: catenary-riser-1-simple-catenary-analysis
description: 'Sub-skill of catenary-riser: 1. Simple Catenary Analysis (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Simple Catenary Analysis (+2)

## 1. Simple Catenary Analysis


```yaml
catenary:
  simple_catenary:
    flag: true
    geometry:
      top_end:
        x: 0.0
        z: 100.0
      touchdown:
        x: 500.0

*See sub-skills for full details.*

## 2. Lazy Wave Catenary


```yaml
catenary:
  lazy_wave:
    flag: true
    geometry:
      water_depth: 1500.0
      hang_off_angle: 8.0
      buoyancy_section:
        start_arc_length: 800.0
        end_arc_length: 1200.0

*See sub-skills for full details.*

## 3. OrcaFlex Model Generation


```yaml
catenary:
  orcaflex_model:
    flag: true
    catenary_config: "results/lazy_wave_config.csv"
    orcaflex_settings:
      line_name: "Riser1"
      segment_length: 5.0
      include_buoyancy_modules: true
    output:
      yml_file: "models/riser_model.yml"
```
