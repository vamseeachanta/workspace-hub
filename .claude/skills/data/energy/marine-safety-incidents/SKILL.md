---
name: marine-safety-incidents
description: Collect, analyze, and report marine safety incident data from 7 global
  maritime authorities. Use for incident scraping, safety trend analysis, risk assessment,
  geographic hotspot identification, and marine safety reporting.
capabilities: []
requires: []
see_also:
- marine-safety-incidents-1-incident-data-collection
- marine-safety-incidents-cli-usage
- marine-safety-incidents-data-sources
- marine-safety-incidents-incident-csv
tags: []
category: data
version: 1.0.0
---

# Marine Safety Incidents

## When to Use

- Marine safety incident data collection and scraping
- Safety trend analysis and risk assessment
- Geographic hotspot identification
- Incident type classification and severity analysis
- Environmental impact assessment from marine incidents
- Regulatory compliance reporting
- Root cause analysis

## Prerequisites

- Python environment with `worldenergydata` package installed
- Database connection (PostgreSQL recommended)
- API keys for relevant data sources (if applicable)

## Python API

### Data Collection

```python
from worldenergydata.marine_safety.scrapers import MarineSafetyScraper
from worldenergydata.marine_safety.database import IncidentDatabase

# Initialize scraper
scraper = MarineSafetyScraper()

# Scrape from specific source
incidents = scraper.scrape(
    source="uscg",

*See sub-skills for full details.*
### Incident Analysis

```python
from worldenergydata.marine_safety.analysis import IncidentAnalyzer

# Initialize analyzer
analyzer = IncidentAnalyzer(database_url="postgresql://...")

# Get trend summary
trends = analyzer.get_trends(
    start_date="2020-01-01",
    end_date="2024-12-31",

*See sub-skills for full details.*
### Geographic Hotspot Detection

```python
from worldenergydata.marine_safety.analysis import GeographicAnalyzer

# Initialize geographic analyzer
geo = GeographicAnalyzer()

# Find hotspots
hotspots = geo.detect_hotspots(
    region="gulf_of_mexico",
    method="dbscan",

*See sub-skills for full details.*
### Risk Scoring

```python
from worldenergydata.marine_safety.analysis import RiskAssessor

# Initialize risk assessor
risk = RiskAssessor()

# Calculate risk scores
scores = risk.calculate_risk(
    vessel_type="offshore_platform",
    region="north_sea",

*See sub-skills for full details.*
### Reporting

```python
from worldenergydata.marine_safety.visualization import SafetyReportGenerator

# Initialize report generator
reporter = SafetyReportGenerator()

# Generate comprehensive report
report = reporter.generate_report(
    start_date="2023-01-01",
    end_date="2023-12-31",

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `MarineSafetyScraper` | Multi-source incident scraping |
| `IncidentDatabase` | Database operations and storage |
| `IncidentAnalyzer` | Statistical analysis and trends |
| `GeographicAnalyzer` | Hotspot detection and mapping |
| `RiskAssessor` | Risk scoring and assessment |
| `SafetyReportGenerator` | HTML/PDF report generation |

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE-specific extraction
- [field-analyzer](../field-analyzer/SKILL.md) - Field-level analysis
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Visualization

## References

- USCG Marine Safety Information Portal
- BSEE Incident Statistics
- IMO GISIS Maritime Casualties Database
- DNV Maritime Safety Standards

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [1. Incident Data Collection (+3)](1-incident-data-collection/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Data Sources](data-sources/SKILL.md)
- [Incident CSV (+1)](incident-csv/SKILL.md)
