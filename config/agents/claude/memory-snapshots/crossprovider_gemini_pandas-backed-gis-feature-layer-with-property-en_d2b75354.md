---
name: crossprovider gemini pandas-backed-gis-feature-layer-with-property-en
description: Pandas-backed GIS feature layer with property encapsulation and GeoJSON bridge
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gis, spatial-data, pandas, geojson, architecture]
---

Lightweight spatial data structure: wrap DataFrame with coordinate column names (lon_col, lat_col) as constructor params with defaults ('longitude', 'latitude'). Use @property for lazy centroid/bounding-box calculation and filter() that returns new FeatureLayer instances. Provide from_geojson() classmethod for FeatureCollection import (extracts Point geometries only, skips others). This design avoids heavy geospatial dependencies while preserving spatial semantics.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
