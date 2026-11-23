---
name: python-gis-ecosystem-checklist
description: 'Sub-skill of python-gis-ecosystem: Checklist (+1).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Checklist (+1)

## Checklist


- [ ] `gdf.crs` matches expected EPSG
- [ ] `gdf.geometry.is_valid.all()` returns True
- [ ] `gdf.shape[0]` matches expected row count
- [ ] Bounding box (`gdf.total_bounds`) falls in correct region
- [ ] Depth samples at known locations match published chart data
- [ ] Reprojection round-trip error < 1 m (project then unproject)
- [ ] Exported file opens in QGIS without errors


## Round-Trip CRS Check


```python
from pyproj import Transformer

t_fwd = Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)
t_rev = Transformer.from_crs("EPSG:32631", "EPSG:4326", always_xy=True)

x_utm, y_utm = t_fwd.transform(-1.5, 57.0)
lon_back, lat_back = t_rev.transform(x_utm, y_utm)
assert abs(lon_back - (-1.5)) < 1e-6, "CRS round-trip failed"
assert abs(lat_back - 57.0) < 1e-6,  "CRS round-trip failed"
```
