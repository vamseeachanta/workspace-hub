---
name: orcaflex-operability-basic-operability-configuration
description: 'Sub-skill of orcaflex-operability: Basic Operability Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Operability Configuration (+1)

## Basic Operability Configuration


```yaml
# configs/operability_config.yml

operability:
  # Input data
  simulation_directory: "results/.sim/"
  file_pattern: "mooring_heading_*.sim"

  # Tension extraction
  line_names:
    - "Mooring_Line_1"
    - "Mooring_Line_2"
    - "Mooring_Line_3"
    - "Mooring_Line_4"
  variable: "Effective Tension"
  statistic: "max"  # max, min, mean

  # Limits for envelope
  tension_limits:
    intact: 2500.0      # kN - intact condition limit
    damaged: 3000.0     # kN - damaged condition limit (typically higher)

  # Wave scatter for downtime
  wave_scatter:
    file: "data/wave_scatter_gom.csv"
    format: "hs_tp_matrix"  # or "hs_tp_list"

  # Output
  output:
    directory: "reports/operability/"
    report_name: "mooring_operability"
    format: "html"  # html, pdf
```


## Advanced Configuration


```yaml
# configs/operability_advanced.yml

operability:
  # Input data
  simulation_directory: "results/calm_operability/.sim/"
  file_pattern: "calm_hs*_tp*_dir*.sim"

  # Multi-line analysis
  line_groups:
    windward:
      lines: ["Leg_1", "Leg_2", "Leg_3"]
      critical_limit: 2000.0
    leeward:
      lines: ["Leg_4", "Leg_5", "Leg_6"]
      critical_limit: 2200.0

  # Heading analysis
  headings:
    start: 0
    end: 360
    step: 15
    critical_count: 5  # Top N critical headings to report

  # Envelope visualization
  envelope:
    polar_plot: true
    include_limits: true
    colorscale: "Viridis"
    show_critical_headings: true

  # Weather downtime
  downtime:
    operational_hours_per_year: 8760
    minimum_window_hours: 6  # Minimum weather window
    include_seasonal: true
    seasons:
      winter: [12, 1, 2]
      spring: [3, 4, 5]
      summer: [6, 7, 8]
      autumn: [9, 10, 11]

  # Output
  output:
    directory: "reports/operability/"
    report_name: "calm_operability_comprehensive"
    include_data_tables: true
    export_csv: true
```
