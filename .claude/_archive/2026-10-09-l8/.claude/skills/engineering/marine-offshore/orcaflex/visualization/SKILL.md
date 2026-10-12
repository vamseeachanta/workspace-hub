---
name: orcaflex-visualization
description: "Generate visualizations from OrcaFlex and OrcaWave simulations using\
  \ the shared OrcFxAPI \u2014 model views (SaveModelView), time series plots, range\
  \ graphs, and interactive HTML reports. Covers both .dat/.sim (OrcaFlex) and .owd\
  \ (OrcaWave) files via the same API surface."
type: reference
version: 1.1.0
updated: 2026-02-23
category: engineering
triggers:
- visualization
- plot results
- model view
- mesh view
- schematic
- time series plot
- range graph
- animation
- HTML report
- interactive plot
- orcawave mesh screenshot
- diffraction mesh view
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Visualization

## When to Use

- Generating model view images for reports
- Creating time series plots of simulation results
- Visualizing range graphs along line arc lengths
- Building interactive HTML dashboards
- Comparing multiple simulations visually
- Animating simulation results
- Capturing diffraction mesh screenshots for OrcaWave validation reports

## Python API

### Model View Generation

```python
from digitalmodel.solvers.orcaflex.opp_visualization import OPPVisualization
from pathlib import Path

def generate_model_views(
    sim_file: str,
    output_dir: str,
    views: list = None
) -> list:
    """

*See sub-skills for full details.*
### Time Series Plotting

```python
import OrcFxAPI
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_time_series(
    sim_file: str,
    variables: list,
    output_file: str = None
) -> go.Figure:

*See sub-skills for full details.*
### Range Graph Plotting

```python
import OrcFxAPI
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_range_graph(
    sim_file: str,
    object_name: str,
    variables: list,

*See sub-skills for full details.*
### Polar Plot for Directional Analysis

```python
import plotly.graph_objects as go
import numpy as np

def create_polar_plot(
    headings: list,
    values: list,
    title: str = "Directional Response",
    output_file: str = None
) -> go.Figure:

*See sub-skills for full details.*
### HTML Report Generation

```python
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime

def generate_html_report(
    title: str,
    sim_file: str,
    figures: list,
    summary_data: dict,

*See sub-skills for full details.*
### Parallel View Generation

```python
from digitalmodel.solvers.orcaflex.opp_visualization import OPPVisualization
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def generate_views_parallel(
    sim_files: list,
    output_dir: str,
    views: list,
    max_workers: int = 4

*See sub-skills for full details.*

## Related Skills

- orcaflex-post-processing - Data extraction
- orcaflex-operability - Envelope visualization
- orcaflex-results-comparison - Comparison plots
- orcaflex-extreme-analysis - Extreme value plots

## References

- Plotly Python Documentation
- OrcaFlex: Post-Processing Views
- OrcaWave WAMIT Validation Guide (Figure 30 — elevation/plan/perspective mesh views)
- Source: `scripts/capture_riser_views.py` (canonical minimal pattern)
- Source: `src/digitalmodel/solvers/orcaflex/pipeline_schematic.py` (`OrcaFlexViewCapture`)
- Source: `src/digitalmodel/solvers/orcaflex/opp_visualization.py` (batch parallel)
- Source: `scripts/build_sme_report.py` (`img_to_base64` HTML embedding)
- Source: `src/digitalmodel/solvers/orcaflex/post_results/postProcessPlotting.py`

## Sub-Skills

- Basic Visualization Configuration (+1)
- Model Views (+2)

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- [[1.1.0] - 2026-02-23 (+1)](110-2026-02-23/SKILL.md)
- OrcaWave Mesh Export via Diffraction (+4)
- Model Views (+1)
- Image Outputs (+1)
