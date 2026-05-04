---
name: gis-informed-workflow-4-failure-diagnosis
description: 'Sub-skill of gis-informed-workflow: 4. FAILURE DIAGNOSIS.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 4. FAILURE DIAGNOSIS

## 4. FAILURE DIAGNOSIS


| Error | Cause | Fix |
|-------|-------|-----|
| Depth profile shows `nan` values | Route extends beyond bathymetry grid | Expand GEE export bounds; check route CRS matches raster CRS |
| Route has gaps / discontinuities | Source shapefile multi-part geometry | Explode and sort by chainage; use `gpd.explode()` |
| Metocean extraction returns all zeros | Wrong variable name in NetCDF | Inspect `ds.data_vars` |
| OrcaFlex environment YAML fails validation | Depth profile non-monotonic | Sort profile by chainage; remove duplicate distances |
| Wells fall outside lease block | CRS mismatch | Ensure both layers in same CRS before `sjoin` |
| GEE export empty | AOI too small at requested scale | Reduce scale to match AOI size |

---
