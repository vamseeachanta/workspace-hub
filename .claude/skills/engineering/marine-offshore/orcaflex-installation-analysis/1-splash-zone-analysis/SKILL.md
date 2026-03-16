---
name: orcaflex-installation-analysis-1-splash-zone-analysis
description: 'Sub-skill of orcaflex-installation-analysis: 1. Splash Zone Analysis
  (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Splash Zone Analysis (+2)

## 1. Splash Zone Analysis


Focus on depths around waterline:

```yaml
delta_elevations:
  - 5     # Above water
  - 2     # Near waterline
  - 0     # At waterline
  - -2    # Just below
  - -5    # Submerged
  - -10   # Below splash zone
```

## 2. Full Lowering Sequence


Complete installation from deck to seabed:

```yaml
delta_elevations:
  - 0     # At deck
  - -5    # Clear of vessel
  - -10   # Splash zone entry
  - -15   # Through splash zone
  - -20   # Mid-water (upper)
  - -30   # Mid-water
  - -50   # Mid-water (lower)
  - -75   # Approaching seabed
  - -95   # Near seabed
  - -100  # At seabed
```

## 3. Landing Sequence


Fine resolution near seabed:

```yaml
# Reference at 5m above seabed
delta_elevations:
  - 0     # 5m above seabed
  - -1    # 4m above
  - -2    # 3m above
  - -3    # 2m above
  - -4    # 1m above
  - -4.5  # 0.5m above (touchdown)
  - -5    # On seabed
```
