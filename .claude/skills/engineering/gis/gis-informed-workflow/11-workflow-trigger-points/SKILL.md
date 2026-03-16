---
name: gis-informed-workflow-11-workflow-trigger-points
description: 'Sub-skill of gis-informed-workflow: 1.1 Workflow Trigger Points (+1).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 1.1 Workflow Trigger Points (+1)

## 1.1 Workflow Trigger Points


| Trigger | GIS Input Required | Downstream Tool |
|---------|-------------------|-----------------|
| Pipeline route analysis | Pipeline centreline .gpkg, bathymetry .tif | digitalmodel, OrcaFlex |
| Riser touch-down zone | Seabed bathymetry near platform, currents | OrcaFlex catenary |
| Well location verification | Well CSV (lat/lon), lease blocks .gpkg | QGIS / GeoPandas |
| Metocean site characterisation | ERA5/GEE wind+wave grids over AOI | digitalmodel |
| Property valuation context | Land registry boundaries, market data pts | assethold (WRK-022) |


## 1.2 Site Characterisation Package (Standard)


Minimum GIS data package for any offshore site:

```python
SITE_PACKAGE = {
    "bathymetry":    "gebco_site_500m.tif",     # depth grid
    "route":         "pipeline_route.gpkg",      # pipeline centreline
    "platform":      "platform_location.geojson",# platform position
    "lease_block":   "lease_block.gpkg",         # licence boundary
    "metocean_grid": "era5_wind_wave_site.nc"    # metocean data
}
```

---
