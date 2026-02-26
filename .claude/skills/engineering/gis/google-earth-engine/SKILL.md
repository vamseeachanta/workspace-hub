---
name: google-earth-engine
version: "1.0.0"
category: engineering/gis
description: "Google Earth Engine AI Interface Skill — ee Python API, authentication,
  image/collection operations, export workflows, GEBCO bathymetry, Sentinel, Landsat"
tags: [gee, google-earth-engine, satellite, remote-sensing, sentinel, landsat, gebco,
       bathymetry, time-series, geemap, marine]
platforms: [linux, windows, macos]
invocation: google-earth-engine
capabilities: [input-generation, execution, output-parsing, failure-diagnosis, validation]
requires: []
see_also: [python-gis-ecosystem, qgis, gis-informed-workflow]
updated: "2026-02-24"
---

# Google Earth Engine AI Interface Skill

```yaml
name: google-earth-engine
version: 1.0.0
category: engineering/gis
created: 2026-02-24
updated: 2026-02-24
description: |
  Full AI-software interface skill for Google Earth Engine (GEE)
  Python API (earthengine-api). Covers authentication, image and
  collection operations, marine datasets (GEBCO, EMODnet, Sentinel),
  time-series analysis, export to Drive/GCS/Asset, and geemap
  integration for visualization.
```

## When to Use This Skill

- Access GEBCO bathymetry, EMODnet seabed, Copernicus marine data
- Sentinel-2 / Landsat optical imagery for site characterisation
- Time-series analysis (wind speed, SST, wave height) over AOI
- Export processed rasters to GeoTIFF for local analysis
- Compute statistics over polygon regions (pipeline corridor, lease block)
- Interactive map visualisation via geemap in Jupyter notebooks

---

## 1. INPUT GENERATION

### 1.1 Authentication

```python
import ee

# First-time setup (opens browser OAuth flow):
# ee.Authenticate()

# Runtime authentication (service account or existing token):
ee.Initialize(project="your-gcp-project-id")

# Service account (CI / headless):
credentials = ee.ServiceAccountCredentials(
    email="sa@project.iam.gserviceaccount.com",
    key_file="/path/to/key.json"
)
ee.Initialize(credentials=credentials, project="your-gcp-project-id")
```

### 1.2 Define Area of Interest (AOI)

```python
import ee

# From bounding box (lon_min, lat_min, lon_max, lat_max)
aoi = ee.Geometry.Rectangle([-5.0, 54.0, 2.0, 60.0])  # North Sea

# From polygon coordinates [[lon, lat], ...]
aoi = ee.Geometry.Polygon([[
    [-2.0, 56.5], [1.5, 56.5], [1.5, 58.0], [-2.0, 58.0]
]])

# From GeoJSON FeatureCollection
aoi = ee.FeatureCollection(
    "projects/my-project/assets/pipeline_corridor"
)
```

### 1.3 Key Marine / Offshore Datasets

| Dataset | EE ID | Description |
|---------|-------|-------------|
| GEBCO 2023 bathymetry | `projects/sat-io/open-datasets/gebco/GEBCO_2023` | Global 15-arc-sec depth |
| ETOPO1 | `NOAA/NGDC/ETOPO1` | Global 1-arc-min elevation |
| Sentinel-2 SR | `COPERNICUS/S2_SR_HARMONIZED` | 10 m optical, 5-day revisit |
| Landsat 8/9 | `LANDSAT/LC09/C02/T1_L2` | 30 m optical |
| ERA5 wind/wave | `ECMWF/ERA5_LAND/HOURLY` | Reanalysis hourly |
| NOAA GOES SST | `NOAA/CDR/OISST/V2_1` | Daily sea surface temp |
| ESA WorldCover | `ESA/WorldCover/v200` | 10 m land cover |

---

## 2. EXECUTION

### 2.1 Load and Clip Bathymetry (GEBCO)

```python
import ee
ee.Initialize(project="your-project")

gebco = ee.Image("projects/sat-io/open-datasets/gebco/GEBCO_2023")
bathy = gebco.select("elevation").clip(aoi)

# Get depth statistics over AOI
stats = bathy.reduceRegion(
    reducer=ee.Reducer.minMax().combine(
        ee.Reducer.mean(), sharedInputs=True
    ),
    geometry=aoi,
    scale=500,              # metres
    maxPixels=1e9
)
print(stats.getInfo())
```

### 2.2 Sentinel-2 Composite (Cloud-Free)

```python
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi)
    .filterDate("2024-06-01", "2024-09-30")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
    .select(["B2", "B3", "B4", "B8"])   # Blue, Green, Red, NIR
    .median()                            # cloud-free composite
    .clip(aoi)
)
```

### 2.3 Time-Series: ERA5 Wind Speed

```python
era5 = (
    ee.ImageCollection("ECMWF/ERA5/DAILY")
    .filterBounds(aoi)
    .filterDate("2023-01-01", "2024-01-01")
    .select(["mean_2m_air_temperature",
             "u_component_of_wind_10m",
             "v_component_of_wind_10m"])
)

# Compute wind speed band
def add_wind_speed(img):
    ws = img.expression(
        "sqrt(u*u + v*v)",
        {"u": img.select("u_component_of_wind_10m"),
         "v": img.select("v_component_of_wind_10m")}
    ).rename("wind_speed")
    return img.addBands(ws)

era5_ws = era5.map(add_wind_speed)
```

### 2.4 Export to GeoTIFF (Google Drive)

```python
task = ee.batch.Export.image.toDrive(
    image=bathy,
    description="gebco_north_sea",
    folder="gee_exports",
    fileNamePrefix="gebco_north_sea_500m",
    region=aoi,
    scale=500,
    crs="EPSG:32631",          # UTM Zone 31N
    maxPixels=1e10,
    fileFormat="GeoTIFF"
)
task.start()

# Poll status
import time
while task.active():
    status = task.status()
    print(f"State: {status['state']}")
    time.sleep(30)
print("Export complete:", task.status()["state"])
```

### 2.5 geemap Visualisation

```python
import geemap

m = geemap.Map(center=[57.0, -1.0], zoom=6)
vis_bathy = {"min": -200, "max": 0, "palette": ["blue", "white"]}
m.addLayer(bathy, vis_bathy, "GEBCO Bathymetry")
m.add_colorbar(vis_bathy, label="Depth (m)")
m.save("north_sea_bathymetry.html")
```

---

## 3. OUTPUT PARSING

### 3.1 Parse getInfo() Results

```python
# Always limit getInfo() to small results — expensive call
result = stats.getInfo()
depth_min = result["elevation_min"]
depth_max = result["elevation_max"]
depth_mean = result["elevation_mean"]
```

### 3.2 Read Exported GeoTIFF

```python
import rasterio
import numpy as np

with rasterio.open("gebco_north_sea_500m.tif") as src:
    depth = src.read(1).astype(float)
    depth[depth == src.nodata] = np.nan
    transform = src.transform
    crs = src.crs
print(f"Grid: {depth.shape}, depth range: {np.nanmin(depth):.0f} to {np.nanmax(depth):.0f} m")
```

### 3.3 Time-Series to DataFrame

```python
import pandas as pd

# Reduce collection to time series at a point
point = ee.Geometry.Point([-1.5, 57.0])
ts = era5_ws.map(lambda img: img.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=point,
    scale=10000
).set("date", img.date().format("YYYY-MM-dd")))

data = ts.aggregate_array("date").getInfo()
ws_vals = ts.aggregate_array("wind_speed").getInfo()
df = pd.DataFrame({"date": data, "wind_speed_ms": ws_vals})
df["date"] = pd.to_datetime(df["date"])
```

---

## 4. FAILURE DIAGNOSIS

| Error | Cause | Fix |
|-------|-------|-----|
| `EEException: Not authenticated` | No valid token | Re-run `ee.Authenticate()` or check service account |
| `EEException: Quota exceeded` | Computation too large | Reduce scale; use `ee.batch.Export` instead of `getInfo()` |
| `getInfo() timeout` | Request too large | Export to Drive; never call `getInfo()` on full images |
| `Dataset not found` | Wrong dataset ID | Check [developers.google.com/earth-engine/datasets](https://developers.google.com/earth-engine/datasets) |
| `Export task FAILED` | Region/scale mismatch; maxPixels exceeded | Increase `maxPixels`; check `region` is valid geometry |
| `Image.select: Band ... not found` | Wrong band name for dataset | Print `image.bandNames().getInfo()` to confirm |
| `No images in collection` | Date range or cloud filter too strict | Widen date range; relax cloud percentage filter |
| `Memory limit exceeded` | Too many pixels in reducer | Increase `scale` parameter; use tiled export |

---

## 5. VALIDATION

### Checklist

- [ ] `ee.Initialize()` succeeds without exception
- [ ] `image.bandNames().getInfo()` returns expected bands
- [ ] `collection.size().getInfo()` > 0 for date/bounds filter
- [ ] Exported GeoTIFF CRS matches requested (`rasterio.open().crs`)
- [ ] Depth values in expected range (e.g., GEBCO: -11000 to +8800 m)
- [ ] Time-series length matches expected date range
- [ ] Spot check: known well location falls within correct depth contour

### Benchmark Check (GEBCO)

```python
# Dogger Bank area should be ~20-40 m depth
test_pt = ee.Geometry.Point([3.0, 55.5])
val = gebco.select("elevation").sample(test_pt, 500).first()
depth_val = val.get("elevation").getInfo()
assert -60 < depth_val < 0, f"GEBCO validation failed: {depth_val}"
```
