---
name: npv-analyzer
description: Perform NPV analysis and economic evaluation for oil & gas assets. Use
  for cash flow modeling, price scenario analysis, Monte Carlo simulation, P10/P50/P90
  probabilistic analysis, working interest calculations, and financial metrics (IRR,
  payback, NPV) for field development projects.
version: 1.0.0
category: data/energy
capabilities: []
requires: []
see_also:
- npv-analyzer-example-1-simple-npv-calculation
- npv-analyzer-model-setup
tags: []
---

# Npv Analyzer

## When to Use

- Calculating NPV for field development projects
- Modeling cash flows with production forecasts
- Running oil/gas price scenario analysis (low/mid/high)
- **Monte Carlo simulation for P10/P50/P90 NPV estimates**
- **Probabilistic risk analysis with multiple input distributions**
- Applying working interest and royalty calculations
- Evaluating different development types (subsea, platform, FPSO)
- Computing IRR, payback period, and profitability index
- **Calculating Value at Risk (VaR) and Expected Shortfall**
- Comparing economic outcomes across multiple scenarios

## Core Pattern

```
Production Forecast → Price Assumptions → Cash Flow Model → Discount → Metrics
```

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
import pandas as pd

class DevelopmentType(Enum):
    """Field development concepts."""

*See sub-skills for full details.*
### NPV Calculator

```python
from typing import List, Dict, Optional
import numpy as np
import numpy_financial as npf

class NPVCalculator:
    """
    Calculate NPV and related economic metrics for oil & gas projects.
    """


*See sub-skills for full details.*
### Scenario Analyzer

```python
from typing import List, Dict
from dataclasses import replace
import pandas as pd

class ScenarioAnalyzer:
    """
    Run multiple NPV scenarios with different price assumptions.
    """


*See sub-skills for full details.*
### Monte Carlo Simulator

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
import pandas as pd

class DistributionType(Enum):
    """Probability distribution types for Monte Carlo inputs."""
    NORMAL = "normal"

*See sub-skills for full details.*
### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class NPVReportGenerator:
    """Generate interactive HTML reports for NPV analysis."""

    def __init__(self, calculator: NPVCalculator,
                 scenario_analyzer: ScenarioAnalyzer = None,

*See sub-skills for full details.*

## YAML Configuration

### Project Configuration

```yaml
# config/npv_analysis.yaml

metadata:
  project_name: "Lower Tertiary Development"
  analyst: "Engineering Team"
  date: "2024-01-15"
  version: "1.0"

economics:

*See sub-skills for full details.*
### Scenario Comparison

```yaml
# config/scenario_comparison.yaml

scenarios:
  - name: "Base Case"
    oil_price: 70
    gas_price: 3.50
    capex_multiplier: 1.0

  - name: "Low Price"

*See sub-skills for full details.*
### Monte Carlo Configuration

```yaml
# config/monte_carlo_analysis.yaml

metadata:
  project_name: "Lower Tertiary Development"
  analyst: "Risk Analysis Team"
  date: "2024-01-15"
  version: "1.0"

monte_carlo:

*See sub-skills for full details.*

## CLI Usage

```bash
# Run NPV analysis
python -m npv_analyzer run --config config/npv_analysis.yaml

# Quick NPV calculation
python -m npv_analyzer calculate \
    --production data/forecast.csv \
    --oil-price 70 \
    --gas-price 3.50 \
    --discount-rate 0.10

# Run scenario comparison
python -m npv_analyzer scenarios --config config/scenario_comparison.yaml

# Calculate breakeven price
python -m npv_analyzer breakeven --config config/npv_analysis.yaml --commodity oil

# Generate sensitivity tornado
python -m npv_analyzer sensitivity --config config/npv_analysis.yaml --range 0.30

# Run Monte Carlo simulation
python -m npv_analyzer montecarlo --config config/monte_carlo_analysis.yaml

# Quick Monte Carlo with default distributions
python -m npv_analyzer montecarlo --config config/npv_analysis.yaml \

*See sub-skills for full details.*

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Production data for forecasts
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - Risk-adjusted NPV with safety data
- [production-forecaster](../production-forecaster/SKILL.md) - Decline curve production forecasts
- [engineering-report-generator](../../development/engineering-report-generator/SKILL.md) - Report generation

## Sub-Skills

- [Example 1: Simple NPV Calculation (+2)](example-1-simple-npv-calculation/SKILL.md)
- [Model Setup (+3)](model-setup/SKILL.md)
