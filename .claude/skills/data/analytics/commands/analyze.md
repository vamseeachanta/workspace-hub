---
name: analyze
type: command
plugin: data
source: https://github.com/anthropics/knowledge-work-plugins
---

# /analyze - Answer Data Questions

Answer data questions ranging from simple lookups to comprehensive reports.

## Usage

```
/analyze <question about your data>
```

## Workflow

### 1. Understand the Question

Parse the user's question to determine complexity:
- **Quick answer**: Single metric, simple filter, straightforward lookup
- **Full analysis**: Multi-dimensional exploration, trend analysis, segmentation
- **Formal report**: Comprehensive investigation with methodology, findings, and recommendations

### 2. Gather Data

If a data warehouse MCP server is connected:
- Explore the schema to find relevant tables
- Write and execute SQL queries to pull the data
- Validate results before presenting

If no warehouse is connected:
- Ask the user to provide data (paste, upload CSV, share a link)
- Work with whatever data format they provide

### 3. Analyze

Depending on the question type:
- Compute the requested metrics
- Identify relevant trends, patterns, or anomalies
- Segment the data if useful for answering the question
- Compare to benchmarks or prior periods where applicable

### 4. Validate

Before presenting results, run quick sanity checks:
- Row counts are reasonable
- Nulls have been handled
- Magnitudes are plausible
- Trends are consistent
- Aggregation logic is correct

### 5. Present

**Quick answers**: State the result directly, include the query for reproducibility.

**Full analyses**: Lead with the key insight, then support with tables and visualizations.

**Formal reports**: Include executive summary, methodology, findings, caveats, and recommendations.

### 6. Visualize (When Appropriate)

If the answer benefits from a chart:
- Choose the right chart type for the data relationship
- Follow the data-visualization skill guidelines
- Create the chart using matplotlib/seaborn or plotly

## Tips

- If the question is ambiguous, clarify before analyzing
- Always note the data freshness (as-of date)
- Flag any data quality issues encountered during analysis
- Offer to go deeper if the initial answer raises new questions
