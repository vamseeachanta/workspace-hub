---
name: orcaflex-environment-config-environment-sanity-checks
description: 'Sub-skill of orcaflex-environment-config: Environment Sanity Checks
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Environment Sanity Checks (+1)

## Environment Sanity Checks


| Parameter | Typical Range | Warning If |
|-----------|---------------|-----------|
| Water depth | 10-3000m | < 0 or > 4000m |
| Hs | 0.5-15m | > 20m or Hs > 0.6 * water_depth |
| Tp | 4-20s | < 3s or > 25s |
| JONSWAP gamma | 1.0-7.0 | < 1 or > 10 |
| Current speed (surface) | 0-3 m/s | > 4 m/s |
| Wind speed (10m ref) | 0-50 m/s | > 60 m/s |
| Seabed stiffness | 10-1000 kN/m/m2 | < 1 or > 10000 |
| Seabed friction | 0.1-1.0 | < 0 or > 2.0 |

## Cross-Validation


```python
def validate_environment(config):
    """Validate environment configuration against physical limits."""
    issues = []

    # Wave steepness check (DNV-RP-C205)
    Hs = config["waves"]["significant_height"]
    Tp = config["waves"]["peak_period"]
    steepness = 2 * 3.14159 * Hs / (9.81 * Tp**2)
    if steepness > 0.07:

*See sub-skills for full details.*
