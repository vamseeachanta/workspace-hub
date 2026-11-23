---
name: pandas-data-processing
version: 1.0.0
description: Pandas for time series analysis, OrcaFlex results processing, and marine
  engineering data workflows
type: reference
author: workspace-hub
category: data
tags:
- pandas
- data-processing
- time-series
- csv
- engineering
- orcaflex
platforms:
- python
capabilities: []
requires: []
---

# Pandas Data Processing

## When to Use This Skill

Use Pandas data processing when you need:
- **Time series analysis** - Wave elevation, vessel motions, mooring tensions
- **OrcaFlex results** - Load simulation results, process RAOs, analyze dynamics
- **Multi-format data** - CSV, Excel, HDF5, Parquet for large datasets
- **Statistical analysis** - Summary statistics, rolling windows, resampling
- **Data transformation** - Pivot, melt, merge, group operations
- **Engineering reports** - Automated data extraction and summary generation

**Avoid when:**
- Real-time streaming data (use Polars or streaming libraries)
- Extremely large datasets (>100GB) - use Dask, Vaex, or PySpark
- Pure numerical computation (use NumPy directly)
- Graph/network data (use NetworkX)

## Complete Examples

### Example 1: OrcaFlex Results Processing

```python
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

def process_orcaflex_results(
    results_dir: Path,
    output_dir: Path
) -> dict:

*See sub-skills for full details.*
### Example 2: Wave Scatter Diagram Analysis

```python
def process_wave_scatter_diagram(
    scatter_csv: Path,
    output_dir: Path
) -> pd.DataFrame:
    """
    Process wave scatter diagram and calculate occurrence frequencies.

    Args:
        scatter_csv: Path to wave scatter CSV

*See sub-skills for full details.*
### Example 3: Fatigue Damage Calculation

```python
def calculate_fatigue_damage(
    stress_ranges: pd.DataFrame,
    sn_curve: dict,
    design_life_years: float = 25
) -> pd.DataFrame:
    """
    Calculate fatigue damage using stress range histogram.

    Args:

*See sub-skills for full details.*
### Example 4: Multi-Source Data Merging

```python
def merge_analysis_results(
    motion_file: Path,
    tension_file: Path,
    environmental_file: Path,
    output_file: Path
) -> pd.DataFrame:
    """
    Merge results from multiple analysis sources.


*See sub-skills for full details.*
### Example 5: Performance Benchmarking

```python
def benchmark_data_processing_methods(
    data_size: int = 1_000_000
) -> pd.DataFrame:
    """
    Benchmark different Pandas operations for performance.

    Args:
        data_size: Number of rows to test


*See sub-skills for full details.*

## Resources

- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Pandas Cheat Sheet**: https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
- **Time Series Analysis**: https://pandas.pydata.org/docs/user_guide/timeseries.html
- **GroupBy Operations**: https://pandas.pydata.org/docs/user_guide/groupby.html
- **Performance Tips**: https://pandas.pydata.org/docs/user_guide/enhancingperf.html

---

**Use this skill for all time series analysis and data processing in DigitalModel!**

## Sub-Skills

- [1. Time Series Analysis](1-time-series-analysis/SKILL.md)
- [2. Statistical Analysis](2-statistical-analysis/SKILL.md)
- [3. Data Transformation](3-data-transformation/SKILL.md)
- [4. Multi-File Processing](4-multi-file-processing/SKILL.md)
- [5. GroupBy Operations](5-groupby-operations/SKILL.md)
- [1. Memory Efficiency (+3)](1-memory-efficiency/SKILL.md)
