---
name: orcaflex-environment-config-common-errors-and-fixes
description: 'Sub-skill of orcaflex-environment-config: Common Errors and Fixes (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Errors and Fixes (+2)

## Common Errors and Fixes


| Error | Cause | Fix |
|-------|-------|-----|
| `Change not allowed for 'WaveGamma'` | WaveGamma only valid for JONSWAP spectrum; set on wrong wave type | Set `WaveSpectrumType` to JONSWAP before setting WaveGamma |
| `Change not allowed for 'SeabedDamping'` | SeabedDamping only valid when `SeabedModel` is set appropriately | Set `SeabedModel` before seabed damping properties |
| `NumberOfCurrentLevels must be >= 2` | Current profile has only 1 depth point | Add at least 2 depth levels (surface + seabed) |
| `WaveHs` vs `WaveHeight` error | Using spectral property name on deterministic wave type | Use `WaveHeight`+`WavePeriod` for Airy/Dean; `WaveHs`+`WaveTp` for JONSWAP/PM |
| Unrealistic vessel drift in statics | Current direction is "from" vs "towards" convention mismatch | OrcaFlex current direction = direction current flows TOWARDS |
| Simulation crashes at startup | Hs too large for water depth (wave breaking) | Check Hs/d ratio; Hs should be < 0.6 * water_depth for shallow water |
| Wave spectrum has no energy at RAO frequencies | Tp too far from vessel natural periods | Ensure wave period range covers vessel response periods (4-25s typical) |

## Mode-Setting Property Order


OrcaFlex requires mode-setting properties to be set BEFORE dependent properties:

```python
# WRONG — gamma set before spectrum type
env.WaveGamma = 3.3
env.WaveSpectrumType = OrcFxAPI.wsJONSWAP  # Too late

# CORRECT — mode first, then dependent properties
env.WaveType = OrcFxAPI.wtIrregular
env.WaveSpectrumType = OrcFxAPI.wsJONSWAP
env.WaveGamma = 3.3  # Now valid
```

## Debugging Environment Issues


```python
def diagnose_environment(model):
    """Check environment configuration for common issues."""
    env = model.environment
    general = model.general
    issues = []

    # Check water depth vs wave height
    wd = general.WaterDepth
    if hasattr(env, 'WaveHs') and env.WaveHs > 0:

*See sub-skills for full details.*
