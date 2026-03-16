---
name: fdas-economics
description: Perform offshore field development economic analysis with NPV, MIRR,
  IRR, and payback calculations. Use for investment analysis, cashflow modeling, BSEE
  data integration, development system classification, and Excel report generation.
capabilities: []
requires: []
see_also:
- fdas-economics-1-financial-metrics-calculation
- fdas-economics-development-systems
- fdas-economics-financial-metrics-json
- fdas-economics-validation
tags: []
category: data
version: 1.0.0
---

# Fdas Economics

## When to Use

- NPV (Net Present Value) calculations for field developments
- MIRR (Modified Internal Rate of Return) analysis
- IRR (Internal Rate of Return) evaluation
- Cashflow modeling for offshore projects
- Development system classification (dry, subsea15, subsea20)
- Production forecasting and analysis
- Drilling timeline extraction and cost modeling
- BSEE data integration for economic analysis
- Excel report generation for stakeholder presentation

## Prerequisites

- Python environment with `worldenergydata` package installed
- BSEE production and well data (optional, for real field analysis)
- Lease assumptions Excel file (optional, for custom assumptions)

## Python API

### Financial Calculations

```python
from worldenergydata.fdas import (
    calculate_npv,
    excel_like_mirr,
    calculate_irr,
    calculate_payback,
    calculate_all_metrics
)
import numpy as np


*See sub-skills for full details.*
### Assumptions Management

```python
from worldenergydata.fdas import AssumptionsManager, classify_dev_system_by_depth

# Load assumptions from Excel
mgr = AssumptionsManager.from_excel('lease_assumptions.xlsx')

# Classify development system by water depth
dev_system = classify_dev_system_by_depth(water_depth=4500)
# Returns: 'subsea15' (500-6000 ft)


*See sub-skills for full details.*
### Production Processing

```python
from worldenergydata.fdas.data import ProductionProcessor
import pandas as pd

# Load production data
production_df = pd.read_csv('production_data.csv')
processor = ProductionProcessor(production_df)

# Monthly aggregation by development
monthly = processor.aggregate_monthly(by='DEV_NAME')

*See sub-skills for full details.*
### Drilling Timeline Extraction

```python
from worldenergydata.fdas.data import DrillingTimelineExtractor

# Extract drilling timeline
extractor = DrillingTimelineExtractor(well_data)

timeline = extractor.extract_timeline(
    development_name='ANCHOR',
    gap_months=3  # Campaign gap threshold
)

print(f"First Spud: {timeline['first_spud']}")
print(f"Last Completion: {timeline['last_completion']}")
print(f"Total Drilling Months: {len(timeline['drilling_monthly'])}")
```
### Cashflow Engine

```python
from worldenergydata.fdas.analysis import CashflowEngine
from datetime import datetime

# Initialize cashflow engine
engine = CashflowEngine(assumptions_mgr, dev_system='subsea15')

# Generate monthly cashflows
cashflows = engine.generate_monthly_cashflow(
    production_monthly=monthly_production,

*See sub-skills for full details.*
### BSEE Data Integration

```python
from worldenergydata.fdas import BseeAdapter
from pathlib import Path

# Initialize BSEE adapter
adapter = BseeAdapter(Path('data/modules/bsee/current'))

# Load data by development
dev_data = adapter.load_by_development('ANCHOR')
production = dev_data['production']

*See sub-skills for full details.*
### Excel Report Generation

```python
from worldenergydata.fdas.reports import FDASReportBuilder

# Generate formatted Excel report
builder = FDASReportBuilder(
    development_name='ANCHOR',
    cashflows=cashflows,
    assumptions=assumptions_mgr,
    dev_system='subsea15'
)

builder.generate_report('anchor_economics.xlsx')
print("Excel report generated: anchor_economics.xlsx")
```
### Complete Workflow Example

```python
from worldenergydata.fdas import (
    AssumptionsManager,
    BseeAdapter,
    calculate_all_metrics
)
from worldenergydata.fdas.data import (
    ProductionProcessor,
    DrillingTimelineExtractor
)

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `calculate_npv` | Net Present Value calculation |
| `excel_like_mirr` | Excel-compatible MIRR calculation |
| `calculate_irr` | Internal Rate of Return calculation |
| `calculate_all_metrics` | Calculate all financial metrics at once |
| `AssumptionsManager` | Load and manage development assumptions |
| `ProductionProcessor` | Process and aggregate production data |
| `DrillingTimelineExtractor` | Extract drilling schedules |
| `CashflowEngine` | Generate monthly cashflow projections |
| `BseeAdapter` | BSEE data loading and integration |
| `FDASReportBuilder` | Excel report generation |

## Related Skills

- [npv-analyzer](../npv-analyzer/SKILL.md) - Simplified NPV calculations
- [production-forecaster](../production-forecaster/SKILL.md) - Production decline curves
- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE data loading

## References

- FDAS V30 Original Implementation
- DNV Financial Analysis Guidelines
- SPE Economic Evaluation Guidelines

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [1. Financial Metrics Calculation (+3)](1-financial-metrics-calculation/SKILL.md)
- [Development Systems](development-systems/SKILL.md)
- [Financial Metrics JSON (+1)](financial-metrics-json/SKILL.md)
- [Validation](validation/SKILL.md)
