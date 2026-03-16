---
name: google-earth-engine-31-parse-getinfo-results
description: 'Sub-skill of google-earth-engine: 3.1 Parse getInfo() Results (+2).'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 3.1 Parse getInfo() Results (+2)

## 3.1 Parse getInfo() Results


```python
# Always limit getInfo() to small results — expensive call
result = stats.getInfo()
depth_min = result["elevation_min"]
depth_max = result["elevation_max"]
depth_mean = result["elevation_mean"]
```


## 3.2 Read Exported GeoTIFF


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


## 3.3 Time-Series to DataFrame


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
