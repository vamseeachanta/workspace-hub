---
name: today-data-sources-configuration
description: 'Sub-skill of today: Data Sources Configuration.'
version: 1.1.0
category: business
type: reference
scripts_exempt: true
---

# Data Sources Configuration

## Data Sources Configuration


Configure in `.Codex/config/today.yaml`:

```yaml
today:
  sources:
    git:
      enabled: true
      lookback_hours: 24
      repos:
        - .  # Current repo

*See sub-skills for full details.*
