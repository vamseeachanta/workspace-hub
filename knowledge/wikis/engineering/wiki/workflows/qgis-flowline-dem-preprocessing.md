---
title: "QGIS flowline alignment and DEM preprocessing"
tags: [qgis, gis, dxf, dem, flowline-alignment, digitalmodel, preprocessing]
sources:
  - ../sources/elements-qgis-flowline-dem-deep-extraction.md
  - /mnt/ace/digitalmodel/tools/qgis
added: 2026-04-28
last_updated: 2026-04-28
domain: engineering
---

# QGIS flowline alignment and DEM preprocessing

The Elements QGIS corpus is a compact reusable workflow/data seed for bringing a flowline alignment and terrain/bathymetry grid into engineering preprocessing.

## Data pattern

- **Alignment**: `18inch Flowline_2.1_align.dxf`, AutoCAD DXF R11/R12, one polyline and 6,102 vertices.
- **Grid**: `dem.tif`, actually ASCII-grid-style content with 12,240 columns and 4,596 rows.
- **Projection**: `dem.prj`, WGS 84 / UTM Zone 15N (`EPSG:32615`).

## Recommended controlled workflow

1. Preserve raw files in `/mnt/ace/digitalmodel/tools/qgis/` as source of record.
2. Normalize the DEM filename/format in a derived workspace, not in-place.
3. Parse the DXF polyline into station/easting/northing points.
4. Sample DEM values along the alignment in EPSG:32615 coordinates.
5. Export a clean CSV/GeoPackage for downstream route profile, free-span, or flowline engineering calculations.
6. Add tests that assert vertex count, grid bounds, projection, and a few sampled station/elevation values.

## Cautions

- The `.tif` suffix is misleading; use content sniffing instead of extension-based assumptions.
- The source grid has substantial `NODATA` coverage (41836462 of 56255040 cells), so route sampling must handle gaps explicitly.
- Do not overwrite raw `/mnt/ace` files; create derived artifacts under a planned digitalmodel workspace.

## Cross-links

- Source extraction: [Deep extraction — Elements QGIS flowline/DEM corpus](../sources/elements-qgis-flowline-dem-deep-extraction.md)
- Catalog page: [Elements ingest catalog — digitalmodel-qgis](../sources/elements-digitalmodel-qgis.md)
