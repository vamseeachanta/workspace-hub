---
name: qgis-checklist
description: 'Sub-skill of qgis: Checklist (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Checklist (+2)

## Checklist


- [ ] Layer loads and `layer.isValid()` returns True
- [ ] Feature count matches expected (`layer.featureCount()`)
- [ ] CRS is correct (`layer.crs().authid()` == expected EPSG)
- [ ] Geometry is valid (run `native:fixgeometries` if not)
- [ ] Well coordinates plot in correct basin/region (visual sanity)
- [ ] Reprojected coordinates match manual calculation spot check
- [ ] Output file size is non-zero and opens in external QGIS GUI


## Coordinate Sanity Check


```python
# Spot check: print first 3 well locations
for feat in layer.getFeatures():
    pt = feat.geometry().asPoint()
    print(f"{feat['well_name']}: lon={pt.x():.4f}, lat={pt.y():.4f}")
    if limit_counter := limit_counter + 1 >= 3:
        break
```


## Marine-Offshore CRS Reference


| Region | UTM Zone | EPSG |
|--------|----------|------|
| North Sea | 31N | 32631 |
| Gulf of Mexico | 15N | 32615 |
| Brazil offshore | 23S–25S | 32723–32725 |
| Australia NW shelf | 50S | 32750 |
| Global (geographic) | WGS84 | 4326 |
| Global (web maps) | Web Mercator | 3857 |
