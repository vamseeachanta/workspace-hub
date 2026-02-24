---
name: qgis
version: "1.0.0"
category: engineering/gis
description: "QGIS AI Interface Skill — PyQGIS headless automation, Processing framework,
  vector/raster I/O, CRS transforms, well plotting from CSV, failure diagnosis"
tags: [qgis, gis, geospatial, pyqgis, vector, raster, crs, coordinate-systems, well-locations]
platforms: [linux, windows, macos]
invocation: qgis
capabilities: [input-generation, execution, output-parsing, failure-diagnosis, validation]
requires: []
see_also: [python-gis-ecosystem, google-earth-engine, gis-informed-workflow]
updated: "2026-02-24"
---

# QGIS AI Interface Skill

```yaml
name: qgis
version: 1.0.0
category: engineering/gis
created: 2026-02-24
updated: 2026-02-24
description: |
  Full AI-software interface skill for QGIS 3.x (LTR).
  Covers PyQGIS headless processing, qgis_process CLI,
  vector/raster operations, CRS handling, well location
  plotting from CSV lat/lon, and offshore/marine GIS workflows.
```

## When to Use This Skill

- Plot well locations from CSV files with lat/lon coordinates
- Reproject vector/raster data between coordinate systems (WGS84, UTM)
- Run QGIS Processing algorithms headlessly (no GUI)
- Perform spatial joins, buffer analysis, and overlay operations
- Export map layouts to PDF, PNG, SVG
- Batch process shapefiles or GeoPackages via PyQGIS scripting

---

## 1. INPUT GENERATION

### 1.1 PyQGIS Application Bootstrap (Headless)

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

### 1.2 Well Locations from CSV (lat/lon)

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

### 1.3 Supported Input Formats

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

## 2. EXECUTION

### 2.1 qgis_process CLI (Headless)

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

### 2.2 Python Processing Framework

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

### 2.3 Common Processing Algorithms

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

## 3. OUTPUT PARSING

### 3.1 Read Features from Output Layer

```python
from qgis.core import QgsVectorLayer

layer = QgsVectorLayer("/data/output.gpkg", "result", "ogr")
features = []
for feat in layer.getFeatures():
    attrs = feat.attributeMap()
    geom = feat.geometry()
    features.append({
        "id":   feat.id(),
        "geom": geom.asWkt(),
        "attrs": {k: v for k, v in attrs.items()}
    })
```

### 3.2 Export to GeoJSON for Downstream Use

```python
from qgis.core import QgsVectorFileWriter, QgsCoordinateTransformContext

error, msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
    layer,
    "/data/wells.geojson",
    QgsCoordinateTransformContext(),
    QgsVectorFileWriter.SaveVectorOptions()
)
if error != QgsVectorFileWriter.WriterError.NoError:
    raise RuntimeError(f"Export failed: {msg}")
```

### 3.3 Raster Statistics

```python
from qgis.analysis import QgsRasterCalculator

# Read raster stats (min/max/mean depth)
from qgis.core import QgsRasterLayer
raster = QgsRasterLayer("/data/bathymetry.tif", "bathy")
provider = raster.dataProvider()
stats = provider.bandStatistics(1)   # band 1
print(f"Depth range: {stats.minimumValue:.1f} to {stats.maximumValue:.1f} m")
```

---

## 4. FAILURE DIAGNOSIS

| Error | Cause | Fix |
|-------|-------|-----|
| `Layer is not valid` | Wrong path, unsupported driver, malformed file | Check path; verify with `ogrinfo`; inspect CRS |
| `QgsApplication not initialized` | Missing `initQgis()` call | Call `qgs.initQgis()` before any QGIS operation |
| `QGIS prefix path not set` | Missing env setup | Set `QgsApplication.setPrefixPath("/usr", True)` or use default |
| `No module named 'qgis'` | QGIS Python not on PYTHONPATH | Run inside QGIS Python console or set `PYTHONPATH` |
| `CRS is not valid / unknown` | EPSG code not found | Use `QgsCoordinateReferenceSystem.fromEpsgId(4326)` |
| Processing `OUTPUT is None` | Algorithm failed silently | Check `feedback.pushWarning()` output; validate inputs |
| `offscreen` platform error | Qt platform missing | Install `libqt5gui5`; set `QT_QPA_PLATFORM=offscreen` |
| Shapefile truncated field names | Shapefile 10-char limit | Export to GeoPackage instead |

---

## 5. VALIDATION

### Checklist

- [ ] Layer loads and `layer.isValid()` returns True
- [ ] Feature count matches expected (`layer.featureCount()`)
- [ ] CRS is correct (`layer.crs().authid()` == expected EPSG)
- [ ] Geometry is valid (run `native:fixgeometries` if not)
- [ ] Well coordinates plot in correct basin/region (visual sanity)
- [ ] Reprojected coordinates match manual calculation spot check
- [ ] Output file size is non-zero and opens in external QGIS GUI

### Coordinate Sanity Check

```python
# Spot check: print first 3 well locations
for feat in layer.getFeatures():
    pt = feat.geometry().asPoint()
    print(f"{feat['well_name']}: lon={pt.x():.4f}, lat={pt.y():.4f}")
    if limit_counter := limit_counter + 1 >= 3:
        break
```

### Marine-Offshore CRS Reference

| Region | UTM Zone | EPSG |
|--------|----------|------|
| North Sea | 31N | 32631 |
| Gulf of Mexico | 15N | 32615 |
| Brazil offshore | 23S–25S | 32723–32725 |
| Australia NW shelf | 50S | 32750 |
| Global (geographic) | WGS84 | 4326 |
| Global (web maps) | Web Mercator | 3857 |
