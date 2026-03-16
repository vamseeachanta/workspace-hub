---
name: well-production-dashboard-command-line-interface
description: 'Sub-skill of well-production-dashboard: Command Line Interface.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Command Line Interface

## Command Line Interface


```bash
# Run dashboard server
python -m worldenergydata.well_production_dashboard.cli run --config config/dashboard.yaml

# Export dashboard
python -m worldenergydata.well_production_dashboard.cli export --format pdf --output reports/export.pdf

# List available options
python -m worldenergydata.well_production_dashboard.cli --help

# Verbose mode for debugging
python -m worldenergydata.well_production_dashboard.cli -v run --config config/dashboard.yaml
```
