---
name: today-installation
description: 'Sub-skill of today: Installation (+1).'
version: 1.1.0
category: business
type: reference
scripts_exempt: true
---

# Installation (+1)

## Installation


```bash
# Make script executable
chmod +x scripts/productivity/daily_today.sh

# Add to crontab (runs at 6 AM daily)
crontab -e
# Add line:
0 6 * * * /path/to/workspace-hub/scripts/productivity/daily_today.sh >> /tmp/daily_today.log 2>&1
```

## Cron Script Features


- Generates daily summary without interactive Claude
- Creates log file in `logs/daily/`
- Can trigger notifications (configurable)
- Supports multiple workspace roots
