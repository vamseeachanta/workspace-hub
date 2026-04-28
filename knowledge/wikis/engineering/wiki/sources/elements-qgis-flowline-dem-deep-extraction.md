---
title: "Deep extraction — Elements QGIS flowline/DEM corpus"
tags: [elements-ingest, qgis, gis, dem, dxf, flowline-alignment, deep-extraction]
sources:
  - /mnt/ace/digitalmodel/tools/qgis/18inch Flowline_2.1_align.dxf
  - /mnt/ace/digitalmodel/tools/qgis/dem.prj
  - /mnt/ace/digitalmodel/tools/qgis/dem.tif
  - workspace-hub#2536
added: 2026-04-28
last_updated: 2026-04-28
domain: engineering
---

# Deep extraction — Elements QGIS flowline/DEM corpus

This page captures the first-pass extraction from the reusable QGIS workflow/data corpus. Raw GIS/CAD files remain in `/mnt/ace/digitalmodel/tools/qgis/`.

## Source files inspected

| File | Size | Type / signal |
|---|---:|---|
| `18inch Flowline_2.1_align.dxf` | 546,567 bytes | AutoCAD DXF R11/R12 alignment geometry |
| `dem.prj` | 599 bytes | WKT projection definition |
| `dem.tif` | 397,944,941 bytes | ASCII-grid style DEM content despite `.tif` suffix |

## Projection

`dem.prj` declares `WGS 84 / UTM zone 15N` with EPSG authority `32615`, meter units, central meridian `-93`, and WGS84 geographic datum.

## DEM grid metadata

| Field | Value |
|---|---:|
| Columns | 12240 |
| Rows | 4596 |
| X lower-left | 184001.55 |
| Y lower-left | 2067807.1 |
| DX | 9.9995237 |
| DY | 9.9986037 |
| NODATA value | -9999.0 |
| Cells read | 56255040 |
| Valid cells | 14418578 |
| NODATA cells | 41836462 |
| Min valid elevation/value | -1415.0 |
| Max valid elevation/value | 65.0 |
| Mean valid elevation/value | -350.547 |

## DXF entity summary

| Entity | Count |
|---|---:|
| `VIEWPORT` | 1 |
| `POLYLINE` | 1 |
| `VERTEX` | 6102 |
| `SEQEND` | 1 |

## Engineering interpretation

- The corpus appears to pair a flowline alignment (`18inch Flowline_2.1_align.dxf`) with a UTM Zone 15N DEM/grid.
- The DXF contains one polyline with 6,102 vertices, suitable for alignment stationing, terrain intersection, route elevation sampling, or GIS-to-engineering preprocessing.
- The DEM file extension is misleading: `file(1)` reports ASCII text and the header uses ESRI ASCII grid-style fields (`NCOLS`, `NROWS`, `XLLCORNER`, `YLLCORNER`, `DX`, `DY`, `NODATA_VALUE`). Treat as a grid text source unless converted/renamed in a controlled workflow.

## Cross-links

- Workflow: [QGIS flowline alignment and DEM preprocessing](../workflows/qgis-flowline-dem-preprocessing.md)
- Catalog page: [Elements ingest catalog — digitalmodel-qgis](elements-digitalmodel-qgis.md)
