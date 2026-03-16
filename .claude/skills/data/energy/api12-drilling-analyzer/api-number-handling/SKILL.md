---
name: api12-drilling-analyzer-api-number-handling
description: 'Sub-skill of api12-drilling-analyzer: API Number Handling (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# API Number Handling (+3)

## API Number Handling

- Always validate API numbers before processing
- Store API numbers as strings to preserve leading zeros
- Use the appropriate format (10, 12, or 14 digit) for your use case
- Group sidetracks with parent wells for proper analysis


## Benchmarking

- Use similar wells (water depth, TD, well type) for accurate comparisons
- Account for learning curve effects when comparing sequential wells
- Consider rig capabilities when benchmarking ROP
- Include NPT analysis to identify improvement opportunities


## AFE Estimation

- Use P50 for planning, P90 for contingency
- Include at least 5-10 analog wells for reliable estimates
- Adjust for rig type and technology differences
- Update estimates as drilling progresses


## File Organization

```
project/
├── config/
│   ├── drilling_analysis.yaml
│   └── afe_estimate.yaml
├── data/
│   ├── bsee_cache/
│   └── results/
│       ├── drilling_analysis.csv
│       └── afe_breakdown.csv
├── reports/
│   ├── drilling_benchmark.html
│   └── well_comparison.html
└── src/
    └── drilling_analyzer/
        ├── api_parser.py
        ├── analyzer.py
        ├── benchmarking.py
        └── reports.py
```
