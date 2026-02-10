---
name: aceengineer-website-update
description: Daily automated website updates with competitor analysis and content sync
version: 1.0.0
category: business
---

# AceEngineer Website Update Skill

Automates daily website maintenance including competitor SEO analysis and content synchronization from related repositories.

## Quick Start

```bash
# Run full daily update
./scripts/daily-update.sh

# Manual competitor analysis
python scripts/competitor_analysis.py

# Manual content sync
python scripts/content_sync.py --digitalmodel ../digitalmodel --worldenergydata ../worldenergydata

# Setup cron job
./scripts/cron-setup.sh
```

## Features

### Competitor Analysis
- Tracks keyword rankings for offshore engineering terms
- Auto-detects competitors from search results
- Generates weekly HTML reports with trends
- Provides SEO improvement recommendations

### Content Sync
- Syncs S-N curve statistics from digitalmodel
- Updates Python module counts
- Imports BSEE production dashboards from worldenergydata
- Generates blog posts from documentation

## Configuration

- `config/keywords.yaml` - Keywords to track
- `config/content-sync.yaml` - Source paths and sync rules

## Outputs

- `reports/competitor-analysis/latest.html` - Latest competitor report
- `assets/data/statistics.json` - Updated site statistics
- `dist/demos/` - Synced demonstration files

## Cron Schedule

Daily at 6 AM local time:
```
0 6 * * * /mnt/github/workspace-hub/aceengineer-website/scripts/daily-update.sh
```

## Dependencies

```bash
pip install pyyaml requests beautifulsoup4
```
