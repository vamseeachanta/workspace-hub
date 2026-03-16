---
name: gis-informed-workflow-21-step-1-fetch-bathymetry-via-gee
description: "Sub-skill of gis-informed-workflow: 2.1 Step 1 \u2014 Fetch Bathymetry\
  \ via GEE (+4)."
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 2.1 Step 1 — Fetch Bathymetry via GEE (+4)

## 2.1 Step 1 — Fetch Bathymetry via GEE


```python
import ee
ee.Initialize(project="your-project")

aoi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
gebco = ee.Image("projects/sat-io/open-datasets/gebco/GEBCO_2023")
bathy = gebco.select("elevation").clip(aoi)

task = ee.batch.Export.image.toDrive(
    image=bathy, description="site_bathymetry",
    folder="gee_exports", fileNamePrefix="site_bathy_500m",
    region=aoi, scale=500, crs="EPSG:32631",
    fileFormat="GeoTIFF", maxPixels=1e10
)
task.start()
# Poll task.active() then download from Drive
```


## 2.2 Step 2 — Extract Depth Profile Along Route


```python
import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString

# Load pipeline route
route = gpd.read_file("pipeline_route.gpkg").to_crs("EPSG:32631")
line = route.geometry.iloc[0]

# Sample bathymetry at regular intervals along route
with rasterio.open("site_bathy_500m.tif") as src:
    distances = np.linspace(0, line.length, 500)
    pts = [line.interpolate(d) for d in distances]
    coords = [(p.x, p.y) for p in pts]
    depths = [v[0] for v in src.sample(coords)]

import pandas as pd
profile = pd.DataFrame({
    "chainage_m": distances,
    "depth_m":    depths
})
profile.to_csv("route_depth_profile.csv", index=False)
```


## 2.3 Step 3 — Metocean Data at Site


```python
import xarray as xr, rioxarray  # noqa
import numpy as np

ds = xr.open_dataset("era5_wind_wave_site.nc")

# Platform position (lon, lat)
plat_lon, plat_lat = 2.5, 57.8

# Extract nearest grid point time series
site_data = ds.sel(
    longitude=plat_lon, latitude=plat_lat,
    method="nearest"
)
wind_speed = np.sqrt(
    site_data["u10"]**2 + site_data["v10"]**2
)
wave_hs = site_data.get("swh")  # Hs if available

metocean_df = site_data.to_dataframe().reset_index()
metocean_df.to_csv("metocean_site.csv", index=False)
```


## 2.4 Step 4 — Build OrcaFlex Environment from GIS


```python
# Translates GIS depth profile + metocean to OrcaFlex environment YAML
# Requires: digitalmodel package

from digitalmodel.offshore.environment import build_orcaflex_environment

env_config = build_orcaflex_environment(
    depth_profile="route_depth_profile.csv",
    metocean_csv="metocean_site.csv",
    return_period=100,              # 100-year extreme
    current_profile="linear"
)
env_config.to_yaml("models/environment.yml")
```


## 2.5 Step 5 — Well Location Verification


```python
import geopandas as gpd
import pandas as pd

# Load wells and lease block
wells = gpd.read_file("wells.csv", layer=None)  # or from_csv
wells_gdf = gpd.GeoDataFrame(
    pd.read_csv("wells.csv"),
    geometry=gpd.points_from_xy(
        pd.read_csv("wells.csv")["longitude"],
        pd.read_csv("wells.csv")["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32631")

lease = gpd.read_file("lease_block.gpkg").to_crs("EPSG:32631")

# Check containment
wells_in_lease = gpd.sjoin(
    wells_gdf, lease, how="left", predicate="within"
)
outside = wells_in_lease[wells_in_lease.index_right.isna()]
if len(outside) > 0:
    print(f"WARNING: {len(outside)} wells outside lease boundary")
```

---
