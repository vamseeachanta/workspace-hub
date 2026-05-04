---
name: google-earth-engine
version: 1.0.0
category: engineering/gis
description: "Google Earth Engine AI Interface Skill \u2014 ee Python API, authentication,\
  \ image/collection operations, export workflows, GEBCO bathymetry, Sentinel, Landsat"
type: reference
tags:
- gee
- google-earth-engine
- satellite
- remote-sensing
- sentinel
- landsat
- gebco
- bathymetry
- time-series
- geemap
- marine
platforms:
- linux
- windows
- macos
invocation: google-earth-engine
capabilities:
- input-generation
- execution
- output-parsing
- failure-diagnosis
- validation
requires: []
updated: '2026-02-24'
scripts_exempt: true
---

# Google Earth Engine

## When to Use This Skill

- Access GEBCO bathymetry, EMODnet seabed, Copernicus marine data
- Sentinel-2 / Landsat optical imagery for site characterisation
- Time-series analysis (wind speed, SST, wave height) over AOI
- Export processed rasters to GeoTIFF for local analysis
- Compute statistics over polygon regions (pipeline corridor, lease block)
- Interactive map visualisation via geemap in Jupyter notebooks

---

## Sub-Skills

- [1.1 Authentication (+2)](11-authentication/SKILL.md)
- [2.1 Load and Clip Bathymetry (GEBCO) (+4)](21-load-and-clip-bathymetry-gebco/SKILL.md)
- [3.1 Parse getInfo() Results (+2)](31-parse-getinfo-results/SKILL.md)
- [4. FAILURE DIAGNOSIS](4-failure-diagnosis/SKILL.md)
- [Checklist (+1)](checklist/SKILL.md)
