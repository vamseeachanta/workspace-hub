---
name: data-analysis-integration-with-workspace-hub
description: 'Sub-skill of data-analysis: Integration with Workspace-Hub.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power data analysis across the workspace-hub ecosystem:

```
workspace-hub/
├── data/
│   ├── pipelines/           # Uses: polars
│   │   ├── etl_pipeline.py
│   │   └── aggregations.py
│   ├── dashboards/          # Uses: streamlit, dash
│   │   ├── streamlit_app/
│   │   └── dash_app/
│   ├── reports/             # Uses: ydata-profiling, great-tables
│   │   ├── quality_reports/
│   │   └── summary_tables/
│   └── eda/                 # Uses: autoviz, sweetviz
│       └── exploration/
├── output/
│   ├── reports/
│   └── exports/
└── config/
    └── analysis_config.yaml
```
