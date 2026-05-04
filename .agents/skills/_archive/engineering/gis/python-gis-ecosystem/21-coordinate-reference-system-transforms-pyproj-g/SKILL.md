---
name: python-gis-ecosystem-21-crs-transforms-pyproj
description: 'Sub-skill of python-gis-ecosystem: 2.1 Coordinate Reference System Transforms
  (pyproj + GeoPandas) (+5).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 2.1 Coordinate Reference System Transforms (pyproj + GeoPandas) (+5)

## 2.1 Coordinate Reference System Transforms (pyproj + GeoPandas)


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


## 2.2 Spatial Operations (Shapely + GeoPandas)


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


## 2.3 Raster Processing (Rasterio)


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


## 2.4 NetCDF / Metocean (xarray + rioxarray)


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


## 2.5 Interactive Map (Folium)


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


## 2.6 Static Map (Cartopy)


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
