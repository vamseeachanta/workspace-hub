---
name: bsee-data-extractor-basic-queries
description: 'Sub-skill of bsee-data-extractor: Basic Queries (+4).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Basic Queries (+4)

## Basic Queries


```bash
# Query by API number
python -m bsee_extractor query --api 1771049130 --output data/well_production.csv

# Query by block
python -m bsee_extractor query --area GC --block 640 --year 2023

# Query multiple years
python -m bsee_extractor query --api 1771049130 --start-year 2010 --end-year 2024
```

## Report Generation


```bash
# Generate well report
python -m bsee_extractor report --api 1771049130 --output reports/well_report.html

# Generate field report from config
python -m bsee_extractor report --config config/field_analysis.yaml
```

## WAR Queries


```bash
# Query WAR data by API number
python -m bsee_extractor war --api 1771049130 --output data/war_well.csv

# Query WAR data by block
python -m bsee_extractor war --area GC --block 640 --output data/war_block.csv

# Filter by activity type
python -m bsee_extractor war --area WR --block 758 --activity drilling,completion

# Generate drilling timeline report
python -m bsee_extractor war-report --area GC --block 640 --output reports/drilling_timeline.html
```

## APD Queries


```bash
# Query APD data by API number
python -m bsee_extractor apd --api 1771049130 --output data/apd_well.csv

# Query APD data by area
python -m bsee_extractor apd --area WR --status approved,pending --output data/apd_area.csv

# Recent APD applications
python -m bsee_extractor apd --area GC --since 2023-01-01 --output data/recent_apd.csv
```

## Data Export


```bash
# Export production to CSV
python -m bsee_extractor export --api 1771049130 --format csv --output data/export.csv

# Export to Parquet (for large datasets)
python -m bsee_extractor export --area GC --block 640 --format parquet --output data/block_production.parquet

# Export combined production + WAR data
python -m bsee_extractor export --api 1771049130 --include-war --format csv --output data/combined.csv
```
