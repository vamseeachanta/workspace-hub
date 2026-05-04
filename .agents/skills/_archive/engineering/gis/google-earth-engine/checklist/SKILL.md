---
name: google-earth-engine-checklist
description: 'Sub-skill of google-earth-engine: Checklist (+1).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Checklist (+1)

## Checklist


- [ ] `ee.Initialize()` succeeds without exception
- [ ] `image.bandNames().getInfo()` returns expected bands
- [ ] `collection.size().getInfo()` > 0 for date/bounds filter
- [ ] Exported GeoTIFF CRS matches requested (`rasterio.open().crs`)
- [ ] Depth values in expected range (e.g., GEBCO: -11000 to +8800 m)
- [ ] Time-series length matches expected date range
- [ ] Spot check: known well location falls within correct depth contour


## Benchmark Check (GEBCO)


```python
# Dogger Bank area should be ~20-40 m depth
test_pt = ee.Geometry.Point([3.0, 55.5])
val = gebco.select("elevation").sample(test_pt, 500).first()
depth_val = val.get("elevation").getInfo()
assert -60 < depth_val < 0, f"GEBCO validation failed: {depth_val}"
```
