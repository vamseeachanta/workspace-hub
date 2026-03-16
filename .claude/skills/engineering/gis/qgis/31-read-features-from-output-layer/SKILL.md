---
name: qgis-31-read-features-from-output-layer
description: 'Sub-skill of qgis: 3.1 Read Features from Output Layer (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 3.1 Read Features from Output Layer (+2)

## 3.1 Read Features from Output Layer


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


## 3.2 Export to GeoJSON for Downstream Use


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


## 3.3 Raster Statistics


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
