---
name: orcaflex-post-processing-efficient-processing
description: 'Sub-skill of orcaflex-post-processing: Efficient Processing (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Efficient Processing (+2)

## Efficient Processing


1. **Use parallel processing** for multiple .sim files
2. **Limit variables** to only those needed
3. **Specify time ranges** to reduce data volume
4. **Use CSV for data analysis**, HTML for reporting


## Data Organization


1. Store summaries in `results/summary/`
2. Store time series in `results/time_series/`
3. Store range graphs in `results/range_graphs/`
4. Use consistent naming: `{case_name}_{variable_type}.{format}`


## Interactive Reports


1. Always use **Plotly** for interactive HTML (mandatory per workspace standards)
2. Include hover tooltips with values
3. Add legend for multi-line plots
4. Use consistent color schemes
