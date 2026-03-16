---
name: bsee-data-extractor
description: Extract and process BSEE (Bureau of Safety and Environmental Enforcement)
  data including production, WAR (Well Activity Reports), and APD (Application for
  Permit to Drill) data. Use for querying production data, well activities, drilling
  permits, completions, and workovers by API number, block, lease, or field with automatic
  data normalization and caching.
version: 1.0.0
category: data/energy
capabilities: []
requires: []
see_also:
- bsee-data-extractor-data-types-supported
- bsee-data-extractor-data-models
- bsee-data-extractor-query-configuration
- bsee-data-extractor-basic-queries
tags: []
---

# Bsee Data Extractor

## When to Use

- Querying BSEE production data by API number, block, or lease
- Downloading and parsing BSEE ZIP file archives
- Normalizing production data across different time periods
- Building production timelines for specific wells or fields
- Tracking well status changes over time
- Preparing data for economic analysis (NPV, decline curves)
- Analyzing Well Activity Reports (WAR) for drilling and completion history
- Tracking drilling operations, workovers, and sidetracks
- Reviewing APD (Application for Permit to Drill) records
- Calculating drilling and completion durations
- Building drilling timelines for rig scheduling analysis

## Related Skills

- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis using BSEE production data
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - HSE incident analysis and safety scoring
- [production-forecaster](../production-forecaster/SKILL.md) - Decline curve analysis using BSEE production
- [economic-sensitivity-analyzer](../economic-sensitivity-analyzer/SKILL.md) - Sensitivity and scenario analysis

## Sub-Skills

- [Example 1: Single Well Analysis (+5)](example-1-single-well-analysis/SKILL.md)
- [Example 7: Combined Production + Activity Analysis](example-7-combined-production-activity-analysis/SKILL.md)
- [Data Caching (+3)](data-caching/SKILL.md)

## Sub-Skills

- [Data Types Supported](data-types-supported/SKILL.md)
- [Data Models (+5)](data-models/SKILL.md)
- [Query Configuration (+3)](query-configuration/SKILL.md)
- [Basic Queries (+4)](basic-queries/SKILL.md)
