---
name: google-earth-engine-11-authentication
description: 'Sub-skill of google-earth-engine: 1.1 Authentication (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 1.1 Authentication (+2)

## 1.1 Authentication


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


## 1.2 Define Area of Interest (AOI)


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


## 1.3 Key Marine / Offshore Datasets


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
