---
name: bsee-data-extractor-query-configuration
description: 'Sub-skill of bsee-data-extractor: Query Configuration (+3).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Query Configuration (+3)

## Query Configuration


```yaml
# config/bsee_query.yaml

metadata:
  task: bsee_data_extraction
  created: "2024-01-15"

query:
  type: by_block  # by_api, by_block, by_lease, by_field


*See sub-skills for full details.*

## WAR Query Configuration


```yaml
# config/war_query.yaml

metadata:
  task: war_data_extraction
  created: "2024-01-15"

query:
  type: by_block  # by_api, by_block, by_area


*See sub-skills for full details.*

## APD Query Configuration


```yaml
# config/apd_query.yaml

metadata:
  task: apd_data_extraction

query:
  type: by_area
  area_code: "WR"  # Walker Ridge


*See sub-skills for full details.*

## Multi-Well Configuration


```yaml
# config/field_analysis.yaml

metadata:
  task: field_analysis
  field_name: "Lower Tertiary Development"

wells:
  - api_number: "1771049130"
    name: "Well A-1"

*See sub-skills for full details.*
