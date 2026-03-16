---
name: bsee-data-extractor-data-caching
description: 'Sub-skill of bsee-data-extractor: Data Caching (+3).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Data Caching (+3)

## Data Caching

- Enable caching to avoid repeated downloads
- Set appropriate expiry for frequently updated data
- Use local cache for development, clear for production runs


## Query Optimization

- Query by year ranges to limit data volume
- Use block/area queries for field-level analysis
- Filter early in pipeline to reduce memory usage


## Error Handling

- Handle missing data periods gracefully
- Log warnings for data quality issues
- Validate API numbers before querying


## File Organization

```
project/
├── config/
│   ├── bsee_query.yaml
│   └── field_analysis.yaml
├── data/
│   ├── bsee_cache/         # Downloaded BSEE files
│   ├── raw/                # Raw extracted data
│   ├── processed/          # Cleaned data
│   └── results/            # Analysis outputs
├── reports/
│   ├── wells/              # Individual well reports
│   └── field_production.html
└── src/
    └── bsee_extractor/
        ├── client.py
        ├── models.py
        ├── aggregator.py
        └── reports.py
```
