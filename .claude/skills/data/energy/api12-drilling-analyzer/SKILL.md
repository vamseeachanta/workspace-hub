---
name: api12-drilling-analyzer
description: Analyze drilling performance and metrics using API 12-digit well numbering
  system. Use for drilling time analysis, cost benchmarking, well comparison, sidetracks
  tracking, and drilling efficiency metrics across GOM fields.
capabilities: []
requires: []
see_also:
- api12-drilling-analyzer-example-1-parse-and-analyze-api-numbers
- api12-drilling-analyzer-api-number-handling
tags: []
category: data
version: 1.0.0
---

# Api12 Drilling Analyzer

## When to Use

- Parsing and validating API well numbers (10, 12, or 14 digit formats)
- Analyzing drilling performance by operator, field, or area
- Benchmarking drilling times and costs across similar wells
- Tracking sidetrack wells and their relationship to parent bores
- Calculating drilling efficiency metrics (ROP, NPT, connection time)
- Comparing deepwater vs. shelf drilling performance
- Identifying drilling hazards by area/block
- Generating drilling AFE (Authorization for Expenditure) estimates

## Core Pattern

```
API Number → Parse/Validate → Query BSEE Data → Analyze Drilling Metrics → Benchmark → Report
```
### API Number Structure

| Digits | Description | Example |
|--------|-------------|---------|
| 1-2 | State Code | 17 = Louisiana (OCS) |
| 3-5 | County/Area Code | 710 = Green Canyon |
| 6-10 | Well Sequence | 49130 |
| 11-12 | Sidetrack Number | 00, 01, 02 |
| 13-14 | Completion Number | 00, 01 (14-digit only) |

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd
import re

class APIFormat(Enum):
    """API number format types."""

*See sub-skills for full details.*
### Drilling Analyzer

```python
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DrillingAnalyzer:

*See sub-skills for full details.*
### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class DrillingReportGenerator:
    """Generate interactive drilling analysis reports."""

    def __init__(self, analyzer: DrillingAnalyzer):
        """

*See sub-skills for full details.*

## YAML Configuration

### Drilling Analysis Configuration

```yaml
# config/drilling_analysis.yaml

metadata:
  task: drilling_performance_analysis
  created: "2024-01-15"

wells:
  # List of API numbers to analyze
  - api: "177104913000"

*See sub-skills for full details.*
### AFE Configuration

```yaml
# config/afe_estimate.yaml

metadata:
  task: afe_estimation
  well_name: "Proposed Well A-1"

target_well:
  area: "Green Canyon"
  block: "640"

*See sub-skills for full details.*

## CLI Usage

### API Number Operations

```bash
# Parse and validate API number
python -m drilling_analyzer parse "177104913001"

# Find all sidetracks for a well
python -m drilling_analyzer sidetracks --api 1771049130

# List wells by area
python -m drilling_analyzer list --area GC --water-depth-min 5000
```
### Benchmarking

```bash
# Benchmark by area
python -m drilling_analyzer benchmark --by area --output reports/area_benchmark.html

# Benchmark by operator
python -m drilling_analyzer benchmark --by operator --min-wells 3

# Generate AFE estimate
python -m drilling_analyzer afe --td 25000 --water-depth 7000 --area GC
```
### Reports

```bash
# Generate comprehensive benchmark report
python -m drilling_analyzer report --config config/drilling_analysis.yaml

# Compare specific wells
python -m drilling_analyzer compare --apis 177104913000,177104913001,177590301100

# Generate efficiency metrics
python -m drilling_analyzer efficiency --output reports/efficiency.csv
```

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Source data for drilling analysis
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis using drilling costs
- [production-forecaster](../production-forecaster/SKILL.md) - Link drilling to production outcomes
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - Safety metrics for drilling operations

## Sub-Skills

- [Example 1: Parse and Analyze API Numbers (+4)](example-1-parse-and-analyze-api-numbers/SKILL.md)
- [API Number Handling (+3)](api-number-handling/SKILL.md)
