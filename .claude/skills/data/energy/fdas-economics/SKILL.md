---
name: fdas-economics
description: Perform offshore field development economic analysis with NPV, MIRR, IRR, and payback calculations. Use for investment analysis, cashflow modeling, BSEE data integration, development system classification, and Excel report generation.
---

# FDAS Economics Skill

Field Development Analysis System (FDAS) for offshore oil & gas economic evaluation with Excel-compatible NPV, MIRR, IRR, and payback calculations.

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

## Analysis Types

### 1. Financial Metrics Calculation

Calculate core investment metrics from cashflows.

```yaml
fdas_economics:
  financial_metrics:
    flag: true
    cashflows:
      type: "array"  # or from_production
      values: [-1500, -500, 200, 800, 1200, 1000, 800, 600, 400, 200]
      units: "MM_USD"
    discount_rate: 0.10
    metrics:
      - npv
      - mirr
      - irr
      - payback
    output:
      summary_file: "results/financial_metrics.json"
      report_file: "results/metrics_report.html"
```

### 2. Development System Classification

Classify fields by water depth for cost estimation.

```yaml
fdas_economics:
  classification:
    flag: true
    water_depths:
      - development: "Field_A"
        depth_ft: 4500
      - development: "Field_B"
        depth_ft: 7200
    output:
      classification_file: "results/dev_system_classification.csv"
```

### 3. Cashflow Modeling

Generate monthly cashflow projections.

```yaml
fdas_economics:
  cashflow_modeling:
    flag: true
    development_name: "ANCHOR"
    assumptions_file: "config/lease_assumptions.xlsx"
    dev_system: "subsea15"
    wti_price: 75.0  # or price_curve file
    analysis_period_years: 20
    output:
      cashflow_file: "results/monthly_cashflows.csv"
      summary_file: "results/cashflow_summary.json"
```

### 4. Complete Field Analysis

End-to-end economic analysis with BSEE data.

```yaml
fdas_economics:
  field_analysis:
    flag: true
    development_name: "ANCHOR"
    bsee_data_path: "data/modules/bsee/current"
    assumptions_file: "config/lease_assumptions.xlsx"
    discount_rate: 0.10
    wti_scenario:
      base: 75.0
      low: 55.0
      high: 95.0
    output:
      excel_report: "results/anchor_economics.xlsx"
      html_report: "results/anchor_analysis.html"
      json_summary: "results/anchor_summary.json"
```

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

# Define cashflows (negative = investment, positive = returns)
cashflows = np.array([-1500, -500, 200, 800, 1200, 1000, 800, 600, 400, 200])
discount_rate = 0.10  # 10%

# Calculate NPV
npv = calculate_npv(cashflows, discount_rate, period='annual')
print(f"NPV: ${npv:,.2f}M")

# Calculate MIRR (Excel-compatible)
mirr_monthly, mirr_annual = excel_like_mirr(cashflows, discount_rate)
print(f"MIRR (Annual): {mirr_annual:.2%}")

# Calculate IRR
irr_monthly, irr_annual = calculate_irr(cashflows)
print(f"IRR (Annual): {irr_annual:.2%}")

# Calculate Payback Period
payback = calculate_payback(cashflows)
print(f"Payback: {payback:.1f} years")

# Calculate all metrics at once
metrics = calculate_all_metrics(cashflows, discount_rate=0.10)
# Returns: {npv, mirr_monthly, mirr_annual, irr_monthly, irr_annual, payback_years}
```

### Assumptions Management

```python
from worldenergydata.fdas import AssumptionsManager, classify_dev_system_by_depth

# Load assumptions from Excel
mgr = AssumptionsManager.from_excel('lease_assumptions.xlsx')

# Classify development system by water depth
dev_system = classify_dev_system_by_depth(water_depth=4500)
# Returns: 'subsea15' (500-6000 ft)

# Get specific assumption parameters
host_capex = mgr.get(dev_system, 'HOST_CAPEX_MM')
surf_per_well = mgr.get(dev_system, 'SURF_PER_WELL_MM')
royalty_rate = mgr.get(dev_system, 'ROYALTY_RATE')
variable_opex = mgr.get(dev_system, 'VARIABLE_OPEX_$/BBL')

print(f"Host CAPEX: ${host_capex}M")
print(f"SURF per well: ${surf_per_well}M")
print(f"Royalty rate: {royalty_rate:.1%}")
```

### Production Processing

```python
from worldenergydata.fdas.data import ProductionProcessor
import pandas as pd

# Load production data
production_df = pd.read_csv('production_data.csv')
processor = ProductionProcessor(production_df)

# Monthly aggregation by development
monthly = processor.aggregate_monthly(by='DEV_NAME')

# First oil identification
first_oil = processor.identify_first_oil(by='DEV_NAME')
print(f"First Oil Date: {first_oil['FIRST_OIL_DATE'].iloc[0]}")

# Cumulative production
cumulative = processor.calculate_cumulative_production(by='DEV_NAME')

# Production statistics
stats = processor.get_production_statistics(by='DEV_NAME')
print(f"Peak Rate: {stats['PEAK_RATE_BBL'].iloc[0]:,.0f} BBL/day")
print(f"Total Production: {stats['TOTAL_OIL_BBL'].iloc[0]:,.0f} BBL")
```

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
    drilling_timeline=timeline,
    wti_prices=wti_price_dict,  # {month_str: price}
    first_oil_date=datetime(2025, 1, 1)
)

# Each cashflow contains:
# - Revenue (oil sales)
# - Royalties
# - OPEX (variable and fixed)
# - CAPEX (drilling, facilities, host)
# - Net cashflow
for cf in cashflows[:3]:
    print(f"{cf.month}: Revenue=${cf.revenue_usd:,.0f}, "
          f"OPEX=${cf.opex_usd:,.0f}, Net=${cf.net_cashflow_usd:,.0f}")
```

### BSEE Data Integration

```python
from worldenergydata.fdas import BseeAdapter
from pathlib import Path

# Initialize BSEE adapter
adapter = BseeAdapter(Path('data/modules/bsee/current'))

# Load data by development
dev_data = adapter.load_by_development('ANCHOR')
production = dev_data['production']
wells = dev_data['wells']

print(f"Production records: {len(production)}")
print(f"Wells: {len(wells)}")

# Load production for date range
production = adapter.load_production(
    start_date='2020-01-01',
    end_date='2024-12-31'
)
```

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
from worldenergydata.fdas.analysis import CashflowEngine
from pathlib import Path
import numpy as np

# 1. Load assumptions
mgr = AssumptionsManager.from_excel('lease_assumptions.xlsx')

# 2. Load BSEE data
adapter = BseeAdapter(Path('data/modules/bsee/current'))
dev_data = adapter.load_by_development('ANCHOR')

# 3. Process production
processor = ProductionProcessor(dev_data['production'])
monthly_production = processor.aggregate_monthly(by='DEV_NAME')

# 4. Extract drilling timeline
extractor = DrillingTimelineExtractor(dev_data['wells'])
timeline = extractor.extract_timeline('ANCHOR')

# 5. Determine development system
water_depth = dev_data['wells']['WATER_DEPTH'].mean()
dev_system = 'subsea15' if water_depth < 6000 else 'subsea20'

# 6. Generate cashflows
engine = CashflowEngine(mgr, dev_system)
wti_prices = {str(m): 75.0 for m in monthly_production['YEAR_MONTH']}
first_oil = processor.identify_first_oil(by='DEV_NAME')['FIRST_OIL_DATE'].iloc[0]

cashflows = engine.generate_monthly_cashflow(
    monthly_production,
    timeline,
    wti_prices,
    first_oil
)

# 7. Calculate financial metrics
cf_array = np.array([cf.net_cashflow_usd for cf in cashflows])
metrics = calculate_all_metrics(cf_array, 0.10)

print(f"NPV (10%): ${metrics['npv']/1e6:,.1f}M")
print(f"MIRR: {metrics['mirr_annual']:.2%}")
print(f"IRR: {metrics['irr_annual']:.2%}")
print(f"Payback: {metrics['payback_years']:.1f} years")
```

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

## Development Systems

| System | Water Depth | Description |
|--------|-------------|-------------|
| `dry` | < 500 ft | Shallow water platforms |
| `subsea15` | 500-6000 ft | Standard subsea tieback |
| `subsea20` | > 6000 ft | Deepwater subsea |

## Output Formats

### Financial Metrics JSON

```json
{
  "development": "ANCHOR",
  "discount_rate": 0.10,
  "npv_mm_usd": 1523.45,
  "mirr_annual": 0.1823,
  "irr_annual": 0.2156,
  "payback_years": 4.2,
  "total_capex_mm": 2500.0,
  "total_revenue_mm": 8500.0,
  "profitability_index": 1.61
}
```

### Cashflow Summary CSV

```csv
month,revenue_mm,royalty_mm,opex_mm,capex_mm,net_cashflow_mm,cumulative_mm
2025-01,45.2,5.9,8.5,0.0,30.8,-1969.2
2025-02,48.5,6.3,8.8,0.0,33.4,-1935.8
2025-03,52.1,6.8,9.2,0.0,36.1,-1899.7
```

## Best Practices

1. **Use Excel-compatible MIRR** - Always use `excel_like_mirr()` for consistency with spreadsheet models
2. **Validate assumptions** - Review assumptions file before running analysis
3. **Check data quality** - Verify BSEE data completeness before economic analysis
4. **Document scenarios** - Track WTI price and discount rate assumptions
5. **Version control** - Keep assumptions files and reports versioned

## Validation

FDAS module validated against original implementation:
- NPV: 100% match
- MIRR: 100% match (0.00e+00 difference)
- Performance: 3x faster than original

## Related Skills

- [npv-analyzer](../npv-analyzer/SKILL.md) - Simplified NPV calculations
- [production-forecaster](../production-forecaster/SKILL.md) - Production decline curves
- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE data loading

## References

- FDAS V30 Original Implementation
- DNV Financial Analysis Guidelines
- SPE Economic Evaluation Guidelines
