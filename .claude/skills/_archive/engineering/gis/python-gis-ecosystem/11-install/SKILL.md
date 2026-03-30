---
name: python-gis-ecosystem-11-install
description: 'Sub-skill of python-gis-ecosystem: 1.1 Install (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 1.1 Install (+2)

## 1.1 Install


```bash
# Conda (recommended — resolves GDAL native deps)
conda install -c conda-forge geopandas rasterio fiona pyproj \
    shapely folium xarray rioxarray cartopy

# pip (ensure GDAL system libs installed first)
pip install geopandas rasterio fiona pyproj shapely folium \
    xarray rioxarray cartopy
```


## 1.2 Format Reference


| Format | Extension | Read | Write | Library |
|--------|-----------|------|-------|---------|
| GeoPackage | .gpkg | Yes | Yes | GeoPandas/Fiona |
| Shapefile | .shp | Yes | Yes | GeoPandas/Fiona |
| GeoJSON | .geojson | Yes | Yes | GeoPandas/Fiona |
| GeoTIFF | .tif | Yes | Yes | Rasterio |
| NetCDF | .nc | Yes | Yes | xarray/rioxarray |
| KML | .kml | Yes | Yes | Fiona (with driver) |
| CSV + lat/lon | .csv | Yes | Yes | GeoPandas (from_csv) |
| GeoParquet | .parquet | Yes | Yes | GeoPandas |


## 1.3 Load Well Locations from CSV


```python
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

df = pd.read_csv("wells.csv")   # columns: well_name, latitude, longitude
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326"              # WGS84 geographic
)
print(gdf.head())
```

---
