---
name: fdas-economics-1-financial-metrics-calculation
description: 'Sub-skill of fdas-economics: 1. Financial Metrics Calculation (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Financial Metrics Calculation (+3)

## 1. Financial Metrics Calculation


Calculate core investment metrics from cashflows.

```yaml
fdas_economics:
  financial_metrics:
    flag: true
    cashflows:
      type: "array"  # or from_production
      values: [-1500, -500, 200, 800, 1200, 1000, 800, 600, 400, 200]
      units: "MM_USD"

*See sub-skills for full details.*

## 2. Development System Classification


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

## 3. Cashflow Modeling


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

## 4. Complete Field Analysis


End-to-end economic analysis with BSEE data.

```yaml
fdas_economics:
  field_analysis:
    flag: true
    development_name: "ANCHOR"
    bsee_data_path: "data/modules/bsee/current"
    assumptions_file: "config/lease_assumptions.xlsx"
    discount_rate: 0.10

*See sub-skills for full details.*
