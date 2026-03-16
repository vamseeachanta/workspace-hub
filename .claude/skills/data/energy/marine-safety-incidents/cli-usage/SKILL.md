---
name: marine-safety-incidents-cli-usage
description: 'Sub-skill of marine-safety-incidents: CLI Usage.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Scrape incident data
python -m worldenergydata.marine_safety.cli scrape --source uscg --year 2023

# Analyze trends
python -m worldenergydata.marine_safety.cli analyze --type trends --output trends.html

# Generate risk report
python -m worldenergydata.marine_safety.cli report --format html --output safety_report.html

# Export data
python -m worldenergydata.marine_safety.cli export --format csv --output incidents.csv
```
