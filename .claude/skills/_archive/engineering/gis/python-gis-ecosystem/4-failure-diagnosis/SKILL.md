---
name: python-gis-ecosystem-4-failure-diagnosis
description: 'Sub-skill of python-gis-ecosystem: 4. FAILURE DIAGNOSIS.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 4. FAILURE DIAGNOSIS

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
