---
name: python-gis-ecosystem
version: 1.0.0
category: engineering/gis
description: "Python GIS Ecosystem Skill \u2014 GDAL/OGR, Fiona, Shapely, Rasterio,\
  \ GeoPandas, pyproj, Folium, xarray/rioxarray, Cartopy \u2014 foundational GIS libraries"
tags:
- geopandas
- shapely
- rasterio
- fiona
- gdal
- pyproj
- folium
- xarray
- rioxarray
- cartopy
- geojson
- geopackage
- netcdf
- geotiff
- geospatial
- python
platforms:
- linux
- windows
- macos
invocation: python-gis
capabilities:
- input-generation
- execution
- output-parsing
- failure-diagnosis
- validation
requires: []
see_also:
- python-gis-ecosystem-11-install
- python-gis-ecosystem-21-coordinate-reference-system-transforms-pyproj-g
- python-gis-ecosystem-31-export-vector-to-file
- python-gis-ecosystem-4-failure-diagnosis
- python-gis-ecosystem-checklist
- python-gis-ecosystem-cross-repo-context
updated: '2026-02-24'
scripts_exempt: true
---

# Python Gis Ecosystem

## When to Use This Skill

- Load and manipulate vector data (wells, pipelines, lease blocks)
- Reproject datasets between coordinate systems
- Process raster data (bathymetry, metocean grids, satellite scenes)
- Spatial joins and buffering in Python without QGIS GUI
- Create interactive web maps (Folium) or static plots (Cartopy)
- Process NetCDF metocean or oceanographic datasets (xarray/rioxarray)
- Property valuation spatial analysis (WRK-022 context)

---

## Sub-Skills

- [1.1 Install (+2)](11-install/SKILL.md)
- [2.1 Coordinate Reference System Transforms (pyproj + GeoPandas) (+5)](21-coordinate-reference-system-transforms-pyproj-g/SKILL.md)
- [3.1 Export Vector to File (+1)](31-export-vector-to-file/SKILL.md)
- [4. FAILURE DIAGNOSIS](4-failure-diagnosis/SKILL.md)
- [Checklist (+1)](checklist/SKILL.md)
- [Cross-Repo Context](cross-repo-context/SKILL.md)
