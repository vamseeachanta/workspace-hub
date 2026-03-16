---
name: marine-safety-incidents-1-incident-data-collection
description: 'Sub-skill of marine-safety-incidents: 1. Incident Data Collection (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Incident Data Collection (+3)

## 1. Incident Data Collection


Scrape and import incident data from multiple sources.

```yaml
marine_safety:
  collection:
    flag: true
    sources:
      - uscg       # US Coast Guard
      - ntsb       # National Transportation Safety Board
      - bsee       # Bureau of Safety and Environmental Enforcement

*See sub-skills for full details.*

## 2. Trend Analysis


Analyze incident trends over time.

```yaml
marine_safety:
  trend_analysis:
    flag: true
    grouping:
      - by_year
      - by_month
      - by_incident_type

*See sub-skills for full details.*

## 3. Geographic Analysis


Identify incident hotspots and high-risk areas.

```yaml
marine_safety:
  geographic_analysis:
    flag: true
    regions:
      - gulf_of_mexico
      - north_sea
      - asia_pacific

*See sub-skills for full details.*

## 4. Risk Assessment


Calculate risk scores for vessel types and operations.

```yaml
marine_safety:
  risk_assessment:
    flag: true
    vessel_types:
      - tanker
      - cargo
      - offshore_platform

*See sub-skills for full details.*
