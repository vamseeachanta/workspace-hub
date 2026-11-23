---
name: orcaflex-rao-import-aqwa-import
description: 'Sub-skill of orcaflex-rao-import: AQWA Import (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# AQWA Import (+1)

## AQWA Import


| Issue | Cause | Solution |
|-------|-------|----------|
| Missing DOFs | AQWA output incomplete | Check AQWA run settings |
| Wrong units | Unit conversion | Specify units in config |
| Truncated data | Large file | Use streaming reader |

## Interpolation


| Issue | Cause | Solution |
|-------|-------|----------|
| Oscillations | Sparse data | Use linear interpolation |
| NaN values | Out of range | Extend source data |
| Poor fit | Non-smooth data | Review source quality |
