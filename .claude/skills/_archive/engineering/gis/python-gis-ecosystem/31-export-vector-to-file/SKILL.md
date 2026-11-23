---
name: python-gis-ecosystem-31-export-vector-to-file
description: 'Sub-skill of python-gis-ecosystem: 3.1 Export Vector to File (+1).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 3.1 Export Vector to File (+1)

## 3.1 Export Vector to File


```python
# GeoPackage (preferred)
gdf_utm.to_file("wells_utm.gpkg", driver="GPKG", layer="wells")

# GeoJSON (web interchange, WGS84 expected)
gdf.to_file("wells.geojson", driver="GeoJSON")

# Shapefile (legacy)
gdf.to_file("wells.shp")
```


## 3.2 Export Raster (Rasterio)


```python
import rasterio
from rasterio.transform import from_bounds

profile = {
    "driver": "GTiff", "dtype": "float32",
    "width": arr.shape[1], "height": arr.shape[0],
    "count": 1, "crs": "EPSG:32631",
    "transform": from_bounds(x_min, y_min, x_max, y_max,
                              arr.shape[1], arr.shape[0]),
    "compress": "lzw", "nodata": -9999
}
with rasterio.open("output.tif", "w", **profile) as dst:
    dst.write(arr.astype("float32"), 1)
```

---
