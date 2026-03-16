---
name: orcaflex-post-processing
description: Post-process OrcaFlex simulation results using OPP (OrcaFlex Post-Process).
  Use for extracting summary statistics, linked statistics, range graphs, time series,
  histograms, and generating interactive HTML reports from .sim files.
updated: '2026-01-07'
capabilities: []
requires: []
see_also:
- orcaflex-post-processing-version-metadata
- orcaflex-post-processing-100-2026-01-07
- orcaflex-post-processing-1-summary-statistics
- orcaflex-post-processing-complete-post-processing-configuration
- orcaflex-post-processing-csv-output
- orcaflex-post-processing-parallel-processing-details
- orcaflex-post-processing-common-vessel-variables
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

# Orcaflex Post Processing

## When to Use

- Extracting summary statistics from simulation results
- Creating range graphs for motion/load envelopes
- Generating time series plots for specific variables
- Computing linked statistics (correlations between variables)
- Creating histogram distributions of results
- Building interactive HTML dashboards from simulation data
- Batch processing multiple .sim files in parallel

## Prerequisites

- OrcaFlex license (for reading .sim files)
- Completed simulations in `.sim/` directory
- Python environment with `digitalmodel` package installed

## Python API

### Basic Post-Processing

```python
from digitalmodel.orcaflex.opp import OrcaFlexPostProcess

# Initialize post-processor
opp = OrcaFlexPostProcess()

# Load configuration
cfg = {
    "orcaflex": {
        "postprocess": {

*See sub-skills for full details.*
### Batch Processing with Parallel Execution

```python
from digitalmodel.orcaflex.opp import OrcaFlexPostProcess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

opp = OrcaFlexPostProcess()

# Get all .sim files
sim_files = list(Path("results/.sim/").glob("*.sim"))


*See sub-skills for full details.*
### Extract Specific Results

```python
from digitalmodel.orcaflex.orcaflex_utilities import OrcaflexUtilities

utils = OrcaflexUtilities()

# Load simulation
model, metadata = utils.get_model_and_metadata("simulation.sim")

# Get time history
line = model["Line1"]

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Fatigue assessment

## References

- OrcaFlex Results Documentation
- OrcFxAPI Python Guide
- Workspace HTML Reporting Standards: `docs/modules/standards/HTML_REPORTING_STANDARDS.md`

## Sub-Skills

- [Efficient Processing (+2)](efficient-processing/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [1. Summary Statistics (+4)](1-summary-statistics/SKILL.md)
- [Complete Post-Processing Configuration (+1)](complete-post-processing-configuration/SKILL.md)
- [CSV Output (+2)](csv-output/SKILL.md)
- [Parallel Processing Details](parallel-processing-details/SKILL.md)
- [Common Vessel Variables (+2)](common-vessel-variables/SKILL.md)
