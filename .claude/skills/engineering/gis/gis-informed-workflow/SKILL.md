---
name: gis-informed-workflow
version: "1.0.0"
category: engineering/gis
description: "GIS-Informed Engineering Workflow — GIS site data to engineering analysis
  inputs. Covers: bathymetry extraction, pipeline routing, well location to OrcaFlex,
  metocean spatial analysis, and property valuation spatial overlays."
tags: [gis, workflow, bathymetry, pipeline-routing, orcaflex, metocean, well-locations,
       digital-model, worldenergydata, assethold, marine-offshore]
platforms: [linux, windows, macos]
invocation: gis-workflow
capabilities: [input-generation, execution, output-parsing, failure-diagnosis, validation]
requires:
  - python-gis-ecosystem
  - google-earth-engine
see_also: [qgis, orcaflex-modeling, cfd-pipeline]
updated: "2026-02-24"
---

# GIS-Informed Engineering Workflow Skill

Cross-program workflow connecting GIS spatial data to engineering analysis inputs.
Implements the WRK-372 workflow: **GIS data → digitalmodel → OrcaFlex**.

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

## 1. INPUT GENERATION

### 1.1 Workflow Trigger Points

| Trigger | GIS Input Required | Downstream Tool |
|---------|-------------------|-----------------|
| Pipeline route analysis | Pipeline centreline .gpkg, bathymetry .tif | digitalmodel, OrcaFlex |
| Riser touch-down zone | Seabed bathymetry near platform, currents | OrcaFlex catenary |
| Well location verification | Well CSV (lat/lon), lease blocks .gpkg | QGIS / GeoPandas |
| Metocean site characterisation | ERA5/GEE wind+wave grids over AOI | digitalmodel |
| Property valuation context | Land registry boundaries, market data pts | assethold (WRK-022) |

### 1.2 Site Characterisation Package (Standard)

Minimum GIS data package for any offshore site:

```python
SITE_PACKAGE = {
    "bathymetry":    "gebco_site_500m.tif",     # depth grid
    "route":         "pipeline_route.gpkg",      # pipeline centreline
    "platform":      "platform_location.geojson",# platform position
    "lease_block":   "lease_block.gpkg",         # licence boundary
    "metocean_grid": "era5_wind_wave_site.nc"    # metocean data
}
```

---

## 2. EXECUTION

### 2.1 Step 1 — Fetch Bathymetry via GEE

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

### 2.2 Step 2 — Extract Depth Profile Along Route

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

### 2.3 Step 3 — Metocean Data at Site

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

### 2.4 Step 4 — Build OrcaFlex Environment from GIS

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

### 2.5 Step 5 — Well Location Verification

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

## 3. OUTPUT PARSING

### Artefacts Produced

| File | Format | Consumer |
|------|--------|----------|
| `route_depth_profile.csv` | CSV chainage + depth | digitalmodel |
| `metocean_site.csv` | CSV time series | digitalmodel |
| `models/environment.yml` | OrcaFlex YAML | OrcaFlex model generator |
| `wells_map.html` | Folium interactive | QA / reporting |
| `site_bathy_500m.tif` | GeoTIFF | QGIS / rasterio |
| `pipeline_route.gpkg` | GeoPackage | QGIS / GeoPandas |

---

## 4. FAILURE DIAGNOSIS

| Error | Cause | Fix |
|-------|-------|-----|
| Depth profile shows `nan` values | Route extends beyond bathymetry grid | Expand GEE export bounds; check route CRS matches raster CRS |
| Route has gaps / discontinuities | Source shapefile multi-part geometry | Explode and sort by chainage; use `gpd.explode()` |
| Metocean extraction returns all zeros | Wrong variable name in NetCDF | Inspect `ds.data_vars` |
| OrcaFlex environment YAML fails validation | Depth profile non-monotonic | Sort profile by chainage; remove duplicate distances |
| Wells fall outside lease block | CRS mismatch | Ensure both layers in same CRS before `sjoin` |
| GEE export empty | AOI too small at requested scale | Reduce scale to match AOI size |

---

## 5. VALIDATION

### Checklist

- [ ] Depth profile covers full route length (chainage_max >= route length)
- [ ] Depth values negative (below sea level) throughout offshore section
- [ ] Metocean time series spans required years (e.g., 1979–2024 for ERA5)
- [ ] OrcaFlex YAML loads without error (`yaml.safe_load()`)
- [ ] Wells contained within lease block (zero outside count)
- [ ] Bathymetry GeoTIFF CRS matches route CRS

### Quick Sanity: Route Length Check

```python
from shapely.ops import unary_union
route_length_m = route.geometry.length.sum()
profile_length_m = profile["chainage_m"].max()
coverage = profile_length_m / route_length_m
assert coverage > 0.98, f"Profile covers only {coverage:.0%} of route"
```
