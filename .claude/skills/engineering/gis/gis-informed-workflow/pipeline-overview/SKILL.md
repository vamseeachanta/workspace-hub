---
name: gis-informed-workflow-pipeline-overview
description: 'Sub-skill of gis-informed-workflow: Pipeline Overview.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Pipeline Overview

## Pipeline Overview


```
GEE / QGIS / Local GIS Data          Python GIS Ecosystem
  (bathymetry, site, routes)  ──►     (geopandas, rasterio)
            │                                  │
     .tif / .gpkg / .geojson          processed geometry/depths
                                               │
                                               ▼
                                      digitalmodel
                                    (pipeline, riser config)
                                               │
                                               ▼
                                         OrcaFlex / AQWA
                                       (structural analysis)
```

---
