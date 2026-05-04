---
name: gis-informed-workflow-checklist
description: 'Sub-skill of gis-informed-workflow: Checklist (+1).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Checklist (+1)

## Checklist


- [ ] Depth profile covers full route length (chainage_max >= route length)
- [ ] Depth values negative (below sea level) throughout offshore section
- [ ] Metocean time series spans required years (e.g., 1979–2024 for ERA5)
- [ ] OrcaFlex YAML loads without error (`yaml.safe_load()`)
- [ ] Wells contained within lease block (zero outside count)
- [ ] Bathymetry GeoTIFF CRS matches route CRS


## Quick Sanity: Route Length Check


```python
from shapely.ops import unary_union
route_length_m = route.geometry.length.sum()
profile_length_m = profile["chainage_m"].max()
coverage = profile_length_m / route_length_m
assert coverage > 0.98, f"Profile covers only {coverage:.0%} of route"
```
