---
name: metrics-review
type: command
plugin: product-management
source: https://github.com/anthropics/knowledge-work-plugins
---

# /metrics-review - Analyze Product Metrics

Analyze product metrics and generate actionable insights.

## Usage

```
/metrics-review [time period] [focus area]
```

## Workflow

### 1. Data Gathering

Collect metrics for the specified period, including comparisons to previous periods and targets. If analytics tools are not connected, request user-provided data.

### 2. Organization

Structure metrics using hierarchy:
- North Star metric at the top
- L1 health indicators (acquisition, activation, engagement, retention, revenue, satisfaction)
- L2 diagnostic metrics for deeper investigation

### 3. Trend Analysis

For each metric, examine:
- Current value and directional trend
- Performance versus targets
- Rate of change
- Anomalies
- Correlations between metrics
- Segment-level drivers

### 4. Generate Review

- **Summary**: Overall product health assessment
- **Metric Scorecard**: Current value, change, target, status for each key metric
- **Trend Analysis**: Notable movements with hypotheses
- **Bright Spots**: What is working well
- **Concerns**: Areas needing attention
- **Recommended Actions**: Specific next steps with owners

### 5. Follow-Up

Offer deeper investigations, dashboard specifications, experiment proposals, or recurring review templates.

## Key Principles

- Absolute numbers without context are useless -- always provide comparative context
- Do not over-attribute causation
- Segment analysis reveals hidden patterns
- Reviews should drive decisions and recommend concrete actions
