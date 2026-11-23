---
name: orcaflex-visualization-basic-visualization-configuration
description: 'Sub-skill of orcaflex-visualization: Basic Visualization Configuration
  (+1).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Visualization Configuration (+1)

## Basic Visualization Configuration


```yaml
# configs/visualization_config.yml

visualization:
  # Model views
  views:
    enabled: true
    output_directory: "images/"
    format: "jpg"
    quality: 95

    view_list:
      - name: "plan_view"
        type: "plan"
        width: 1920
        height: 1080

      - name: "elevation_view"
        type: "elevation"
        plane: "XZ"
        width: 1920
        height: 1080

      - name: "3d_view"
        type: "3d"
        azimuth: 45
        elevation: 30
        width: 1920
        height: 1080

  # Time series plots
  time_series:
    enabled: true
    output_directory: "plots/time_series/"
    format: "html"   # Interactive Plotly

    variables:
      - object: "Mooring_Line_1"
        variable: "Effective Tension"
        label: "Line 1 Tension (kN)"

      - object: "Vessel"
        variable: "Heave"
        label: "Vessel Heave (m)"

  # Range graphs
  range_graphs:
    enabled: true
    output_directory: "plots/range_graphs/"

    objects:
      - name: "Riser"
        variables:
          - "Effective Tension"
          - "Curvature"
          - "Bend Moment"

  # HTML report
  report:
    enabled: true
    output_file: "reports/analysis_report.html"
    title: "OrcaFlex Analysis Report"
    include_summary: true
    include_plots: true
    include_tables: true
```


## Advanced Visualization Configuration


```yaml
# configs/visualization_advanced.yml

visualization:
  # View styling
  view_style:
    background_color: "white"
    sea_surface:
      visible: true
      style: "transparent"
      color: [0, 100, 200, 128]  # RGBA
    seabed:
      visible: true
      style: "solid"
      color: [139, 119, 101]
    objects:
      line_width: 2
      vessel_color: [200, 0, 0]

  # Multiple viewpoints
  viewpoints:
    - name: "bow_view"
      centre_on: "Vessel"
      direction: [1, 0, 0]
      distance: 500

    - name: "stern_view"
      centre_on: "Vessel"
      direction: [-1, 0, 0]
      distance: 500

    - name: "touchdown"
      position: [800, 0, -1450]
      target: "Riser"
      arc_length: 1200

  # Plot styling
  plot_style:
    template: "plotly_white"
    font_family: "Arial"
    font_size: 14
    title_font_size: 18
    color_palette: "viridis"

  # Comparison plots
  comparison:
    enabled: true
    simulations:
      - path: "results/baseline.sim"
        label: "Baseline"
        color: "blue"
      - path: "results/modified.sim"
        label: "Modified"
        color: "red"

    variables:
      - object: "Line_1"
        variable: "Effective Tension"
```
