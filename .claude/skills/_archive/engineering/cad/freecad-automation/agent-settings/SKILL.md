---
name: freecad-automation-agent-settings
description: 'Sub-skill of freecad-automation: Agent Settings (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Agent Settings (+1)

## Agent Settings


```json
{
  "settings": {
    "parallel_workers": 4,
    "max_workers": 8,
    "cache_enabled": true,
    "cache_size_mb": 500,
    "auto_save": true,
    "auto_save_interval": 300,
    "validation_level": "strict",
    "error_recovery": true,
    "retry_attempts": 3,
    "timeout_seconds": 600
  }
}
```


## Marine Engineering Settings


```json
{
  "marine_engineering": {
    "units": "metric",
    "standards": ["DNV", "ABS", "API"],
    "vessel_types": ["FPSO", "FSO", "FLNG", "Semi-sub", "TLP", "Spar"],
    "analysis_types": ["stability", "mooring", "structural", "hydrodynamic"]
  }
}
```
