---
name: google-earth-engine-21-load-and-clip-bathymetry-gebco
description: 'Sub-skill of google-earth-engine: 2.1 Load and Clip Bathymetry (GEBCO)
  (+4).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 2.1 Load and Clip Bathymetry (GEBCO) (+4)

## 2.1 Load and Clip Bathymetry (GEBCO)


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


## 2.2 Sentinel-2 Composite (Cloud-Free)


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


## 2.3 Time-Series: ERA5 Wind Speed


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


## 2.4 Export to GeoTIFF (Google Drive)


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


## 2.5 geemap Visualisation


```python
import geemap

m = geemap.Map(center=[57.0, -1.0], zoom=6)
vis_bathy = {"min": -200, "max": 0, "palette": ["blue", "white"]}
m.addLayer(bathy, vis_bathy, "GEBCO Bathymetry")
m.add_colorbar(vis_bathy, label="Depth (m)")
m.save("north_sea_bathymetry.html")
```

---
