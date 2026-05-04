---
name: qgis-11-pyqgis-application-bootstrap-headless
description: 'Sub-skill of qgis: 1.1 PyQGIS Application Bootstrap (Headless) (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 1.1 PyQGIS Application Bootstrap (Headless) (+2)

## 1.1 PyQGIS Application Bootstrap (Headless)


```python
import sys
import os

# Required: set QGIS prefix path before importing
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # headless mode
from qgis.core import QgsApplication

qgs = QgsApplication([], False)  # False = no GUI
qgs.initQgis()

# Always call at end of script:
# qgs.exitQgis()
```


## 1.2 Well Locations from CSV (lat/lon)


```python
from qgis.core import (QgsVectorLayer, QgsProject,
                        QgsCoordinateReferenceSystem)

# CSV with columns: well_name,latitude,longitude
uri = (
    "file:///path/to/wells.csv"
    "?delimiter=,"
    "&xField=longitude"
    "&yField=latitude"
    "&crs=EPSG:4326"          # WGS84 geographic
)
layer = QgsVectorLayer(uri, "wells", "delimitedtext")
if not layer.isValid():
    raise RuntimeError("Failed to load CSV layer")
QgsProject.instance().addMapLayer(layer)
```


## 1.3 Supported Input Formats


| Format | Driver | Use |
|--------|--------|-----|
| GeoPackage (.gpkg) | GPKG | Preferred vector store |
| Shapefile (.shp) | ESRI Shapefile | Legacy vector |
| GeoJSON (.geojson) | GeoJSON | Web interchange |
| GeoTIFF (.tif) | GTiff | Raster standard |
| NetCDF (.nc) | netCDF | Metocean/bathymetry |
| KML (.kml) | KML | Google Earth exchange |
| CSV + lat/lon | delimitedtext | Point data import |

---
