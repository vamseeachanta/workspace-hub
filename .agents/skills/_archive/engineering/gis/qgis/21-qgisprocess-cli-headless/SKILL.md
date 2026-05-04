---
name: qgis-21-qgisprocess-cli-headless
description: 'Sub-skill of qgis: 2.1 qgis_process CLI (Headless) (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 2.1 qgis_process CLI (Headless) (+2)

## 2.1 qgis_process CLI (Headless)


```bash
# List available algorithms
qgis_process list

# Run an algorithm
qgis_process run native:buffer \
  --INPUT=/data/wells.gpkg \
  --DISTANCE=5000 \
  --SEGMENTS=36 \
  --OUTPUT=/data/wells_5km_buffer.gpkg

# Run with JSON params file
qgis_process run native:reprojectlayer \
  --parameters=reproject_params.json
```


## 2.2 Python Processing Framework


```python
import processing
from qgis.core import QgsVectorLayer

# Reproject wells to UTM Zone 31N (offshore NW Europe)
result = processing.run("native:reprojectlayer", {
    "INPUT":      layer,
    "TARGET_CRS": QgsCoordinateReferenceSystem("EPSG:32631"),
    "OUTPUT":     "memory:"
})
utm_layer = result["OUTPUT"]

# Buffer: 500 m radius around each well
result = processing.run("native:buffer", {
    "INPUT":    utm_layer,
    "DISTANCE": 500,
    "SEGMENTS": 32,
    "OUTPUT":   "/data/well_exclusion_zones.gpkg"
})
```


## 2.3 Common Processing Algorithms


| Algorithm | ID | Use |
|-----------|----|-----|
| Reproject | `native:reprojectlayer` | CRS transform |
| Buffer | `native:buffer` | Proximity zones |
| Spatial join | `native:joinattributesbylocation` | Overlay |
| Clip | `native:clip` | Mask to AOI |
| Merge layers | `native:mergevectorlayers` | Combine datasets |
| Raster clip | `gdal:cliprasterbymasklayer` | Crop bathymetry |
| Contour | `gdal:contour` | Depth contours |

---
