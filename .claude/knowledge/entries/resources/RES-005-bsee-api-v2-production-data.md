---
id: RES-005
type: resource
entry_type: reference
title: "BSEE production data available via data.gov API v2"
category: data
domain:
  primary: energy_data
  sub_domain: production_data
tags: [bsee, api, production, oil-gas, data-gov, gulf-of-mexico]
repos: [worldenergydata]
confidence: 0.90
created: "2026-03-25"
last_validated: "2026-03-25"
source:
  name: "BSEE Production Data API (data.gov)"
  source_kind: webpage
  url: "https://www.data.bsee.gov/Main/HtmlPage.aspx?page=publicInfo"
  retrieved: "2026-03-25"
provenance:
  method: manual
  reviewed_by: vamsee
  review_date: "2026-03-25"
related: []
ttl_days: 180
status: active
access_count: 0
file: ".claude/knowledge/entries/resources/RES-005-bsee-api-v2-production-data.md"
---

# RES-005: BSEE production data via data.gov API v2

## Reference
The Bureau of Safety and Environmental Enforcement (BSEE) provides Gulf of Mexico production data through a public API:

- **Query by**: API number, OCS block, lease number, or field name
- **Data includes**: monthly oil/gas/water production, well counts, platform info
- **Format**: JSON responses, CSV bulk downloads available
- **Coverage**: All OCS (Outer Continental Shelf) Gulf of Mexico production

## worldenergydata Integration
The `bsee-data-extractor` skill wraps this API with caching and provides:
- Field-level aggregation from well-level data
- Historical production trend analysis
- Cross-reference with EIA national statistics
- SODIR (Norway) comparison workflows
