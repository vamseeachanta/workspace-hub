---
name: variance-analysis-three-way-comparison-framework
description: 'Sub-skill of variance-analysis: Three-Way Comparison Framework (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Three-Way Comparison Framework (+3)

## Three-Way Comparison Framework


| Metric | Budget | Forecast | Actual | Bud Var ($) | Bud Var (%) | Fcast Var ($) | Fcast Var (%) |
|--------|--------|----------|--------|-------------|-------------|---------------|---------------|
| Revenue | $X | $X | $X | $X | X% | $X | X% |
| COGS | $X | $X | $X | $X | X% | $X | X% |
| Gross Profit | $X | $X | $X | $X | X% | $X | X% |


## When to Use Each Comparison


- **Actual vs Budget:** Annual performance measurement, compensation decisions, board reporting. Budget is set at the beginning of the year and typically not changed.
- **Actual vs Forecast:** Operational management, identifying emerging issues. Forecast is updated periodically (monthly or quarterly) to reflect current expectations.
- **Forecast vs Budget:** Understanding how expectations have changed since planning. Useful for identifying planning accuracy issues.
- **Actual vs Prior Period:** Trend analysis, sequential performance. Useful when budget is not meaningful (new business lines, post-acquisition).
- **Actual vs Prior Year:** Year-over-year growth analysis, seasonality-adjusted comparison.


## Forecast Accuracy Analysis


Track how accurate forecasts are over time to improve planning:

```
Forecast Accuracy = 1 - |Actual - Forecast| / |Actual|

MAPE (Mean Absolute Percentage Error) = Average of |Actual - Forecast| / |Actual| across periods
```

| Period | Forecast | Actual | Variance | Accuracy |
|--------|----------|--------|----------|----------|
| Jan    | $X       | $X     | $X (X%)  | XX%      |
| Feb    | $X       | $X     | $X (X%)  | XX%      |
| ...    | ...      | ...    | ...      | ...      |
| **Avg**|          |        | **MAPE** | **XX%**  |


## Variance Trending


Track how variances evolve over the year to identify systematic bias:

- **Consistently favorable:** Budget may be too conservative (sandbagging)
- **Consistently unfavorable:** Budget may be too aggressive or execution issues
- **Growing unfavorable:** Deteriorating performance or unrealistic targets
- **Shrinking variance:** Forecast accuracy improving through the year (normal pattern)
- **Volatile:** Unpredictable business or poor forecasting methodology
