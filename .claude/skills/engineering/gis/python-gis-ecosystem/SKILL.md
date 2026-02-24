---
name: python-gis-ecosystem
version: "1.0.0"
category: engineering/gis
description: "Python GIS Ecosystem Skill — GDAL/OGR, Fiona, Shapely, Rasterio,
  GeoPandas, pyproj, Folium, xarray/rioxarray, Cartopy — foundational GIS libraries"
tags: [geopandas, shapely, rasterio, fiona, gdal, pyproj, folium, xarray, rioxarray,
       cartopy, geojson, geopackage, netcdf, geotiff, geospatial, python]
platforms: [linux, windows, macos]
invocation: python-gis
capabilities: [input-generation, execution, output-parsing, failure-diagnosis, validation]
requires: []
see_also: [qgis, google-earth-engine, gis-informed-workflow]
updated: "2026-02-24"
---

# Python GIS Ecosystem Skill

```yaml
name: python-gis-ecosystem
version: 1.0.0
category: engineering/gis
created: 2026-02-24
updated: 2026-02-24
description: |
  Foundational Python GIS library skill covering GDAL/OGR, Fiona,
  Shapely, Rasterio, GeoPandas, pyproj, Folium, xarray/rioxarray,
  and Cartopy. These underpin all local GIS workflows — used when
  GEE is not needed or when offline/local processing is required.
```

## When to Use This Skill

- Load and manipulate vector data (wells, pipelines, lease blocks)
- Reproject datasets between coordinate systems
- Process raster data (bathymetry, metocean grids, satellite scenes)
- Spatial joins and buffering in Python without QGIS GUI
- Create interactive web maps (Folium) or static plots (Cartopy)
- Process NetCDF metocean or oceanographic datasets (xarray/rioxarray)
- Property valuation spatial analysis (WRK-022 context)

---

## 1. INPUT GENERATION

### 1.1 Install

```bash
# Conda (recommended — resolves GDAL native deps)
conda install -c conda-forge geopandas rasterio fiona pyproj \
    shapely folium xarray rioxarray cartopy

# pip (ensure GDAL system libs installed first)
pip install geopandas rasterio fiona pyproj shapely folium \
    xarray rioxarray cartopy
```

### 1.2 Format Reference

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

### 1.3 Load Well Locations from CSV

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

## 2. EXECUTION

### 2.1 Coordinate Reference System Transforms (pyproj + GeoPandas)

```python
import geopandas as gpd

# Reproject wells to UTM Zone 31N (North Sea)
gdf_utm = gdf.to_crs("EPSG:32631")

# pyproj direct transform (for arrays)
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32631",
                                    always_xy=True)
x_utm, y_utm = transformer.transform(df["longitude"].values,
                                      df["latitude"].values)
```

### 2.2 Spatial Operations (Shapely + GeoPandas)

```python
import geopandas as gpd

# Buffer 500 m around wells (must be in projected CRS)
gdf_utm["geometry_buffer"] = gdf_utm.geometry.buffer(500)

# Spatial join: which lease blocks contain wells?
lease_blocks = gpd.read_file("lease_blocks.gpkg")
joined = gpd.sjoin(gdf_utm, lease_blocks,
                   how="left", predicate="within")

# Dissolve: merge overlapping buffers
merged = gdf_utm.set_geometry("geometry_buffer").dissolve()
```

### 2.3 Raster Processing (Rasterio)

```python
import rasterio
import numpy as np

with rasterio.open("bathymetry.tif") as src:
    depth = src.read(1).astype(float)
    depth[depth == src.nodata] = np.nan
    transform = src.transform   # affine transform
    crs = src.crs

# Extract depth at well locations
from rasterio.sample import sample_gen
coords = list(zip(gdf_utm.geometry.x, gdf_utm.geometry.y))
sampled = list(sample_gen(rasterio.open("bathymetry.tif"), coords))
gdf_utm["depth_m"] = [s[0] for s in sampled]
```

### 2.4 NetCDF / Metocean (xarray + rioxarray)

```python
import xarray as xr
import rioxarray    # noqa: F401 — registers .rio accessor

ds = xr.open_dataset("era5_wind.nc")
u10 = ds["u10"]                       # eastward wind component
v10 = ds["v10"]                       # northward wind component
ws  = np.sqrt(u10**2 + v10**2).rename("wind_speed")

# Clip to AOI (after setting spatial dims)
ds_clipped = ds.rio.set_spatial_dims("longitude", "latitude")
ds_clipped = ds_clipped.rio.write_crs("EPSG:4326")
ds_clipped = ds_clipped.rio.clip_box(
    minx=-5.0, miny=54.0, maxx=2.0, maxy=60.0
)
```

### 2.5 Interactive Map (Folium)

```python
import folium

m = folium.Map(location=[57.0, -1.0], zoom_start=6,
               tiles="CartoDB positron")

# Add well markers
for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5, color="red", fill=True,
        popup=row.get("well_name", "well")
    ).add_to(m)

m.save("wells_map.html")
```

### 2.6 Static Map (Cartopy)

```python
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig, ax = plt.subplots(
    figsize=(10, 8),
    subplot_kw={"projection": ccrs.Mercator()}
)
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.set_extent([-5, 2, 54, 60], crs=ccrs.PlateCarree())
ax.scatter(
    gdf.geometry.x, gdf.geometry.y,
    transform=ccrs.PlateCarree(), s=20, c="red", zorder=5
)
plt.savefig("wells_map.png", dpi=150, bbox_inches="tight")
```

---

## 3. OUTPUT PARSING

### 3.1 Export Vector to File

```python
# GeoPackage (preferred)
gdf_utm.to_file("wells_utm.gpkg", driver="GPKG", layer="wells")

# GeoJSON (web interchange, WGS84 expected)
gdf.to_file("wells.geojson", driver="GeoJSON")

# Shapefile (legacy)
gdf.to_file("wells.shp")
```

### 3.2 Export Raster (Rasterio)

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

## 4. FAILURE DIAGNOSIS

| Error | Cause | Fix |
|-------|-------|-----|
| `CRS mismatch in spatial join` | Layers in different CRS | Reproject both to same CRS before join |
| `GDAL not found` / `import rasterio` fails | GDAL native libs missing | Use `conda install -c conda-forge rasterio` |
| `ValueError: No CRS set` | GeoDataFrame has no CRS | Set via `gdf = gdf.set_crs("EPSG:4326")` |
| `TopologicalError` (Shapely) | Invalid geometry | Run `gdf.geometry = gdf.geometry.buffer(0)` to fix |
| `Nodata values appear as valid data` | nodata not masked | Use `rasterio.open().read(masked=True)` |
| `MemoryError` on large raster | Full raster in RAM | Use windowed reading: `rasterio.open().block_windows()` |
| `xarray KeyError: variable` | Wrong variable name | Inspect with `ds.data_vars` |
| `fiona.errors.DriverError` | KML needs LIBKML driver | Install `fiona[all]` or use `gpd.read_file(..., driver='KML')` |

---

## 5. VALIDATION

### Checklist

- [ ] `gdf.crs` matches expected EPSG
- [ ] `gdf.geometry.is_valid.all()` returns True
- [ ] `gdf.shape[0]` matches expected row count
- [ ] Bounding box (`gdf.total_bounds`) falls in correct region
- [ ] Depth samples at known locations match published chart data
- [ ] Reprojection round-trip error < 1 m (project then unproject)
- [ ] Exported file opens in QGIS without errors

### Round-Trip CRS Check

```python
from pyproj import Transformer

t_fwd = Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)
t_rev = Transformer.from_crs("EPSG:32631", "EPSG:4326", always_xy=True)

x_utm, y_utm = t_fwd.transform(-1.5, 57.0)
lon_back, lat_back = t_rev.transform(x_utm, y_utm)
assert abs(lon_back - (-1.5)) < 1e-6, "CRS round-trip failed"
assert abs(lat_back - 57.0) < 1e-6,  "CRS round-trip failed"
```

## Cross-Repo Context

| Repo | GIS Usage |
|------|-----------|
| `worldenergydata` | GeoPandas for energy asset location data, CRS transforms |
| `assethold` | Property valuation spatial analysis (WRK-022), lease boundary overlays |
| `digitalmodel` | Pipeline routing geometry, riser base location, metocean spatial grids |
