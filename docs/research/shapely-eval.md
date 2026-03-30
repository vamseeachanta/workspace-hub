# Shapely 2.x Evaluation — Planar Geometry for Site Layout

**Issue:** workspace-hub#1491
**Date:** 2026-03-29
**Version evaluated:** 2.1.2 (stable), GEOS 3.11.4

---

## Summary

Shapely 2.x is a mature, stable planar geometry library that exposes GEOS operations as
NumPy ufuncs, delivering 4–100x speedups over the scalar 1.x API. It is the de-facto
standard for Python GIS geometry and is natively integrated by GeoPandas, pyproj, and
Rasterio. For offshore/marine site layout work — exclusion zones, cable corridors, turbine
spacing polygons, and distance queries — it provides exactly the right primitive operations
with pre-built binary wheels that bundle GEOS.

---

## Key v2.x Features

| Feature | v1.x | v2.x |
|---|---|---|
| Vectorized ops (ufuncs) | No — Python loops required | Yes — all ops accept NumPy arrays |
| Performance vs. 1.x | Baseline | 4–100x faster; lightweight ops gain most |
| GIL release | No | Yes — true multi-thread GEOS execution |
| GEOS context overhead | Re-init per call | Thread-local reuse (v2.2+, ~75 ns saved/call) |
| Top-level imports | `from shapely.geometry import Polygon` | `from shapely import Polygon` |
| `shapely.vectorized` module | Provided `contains`, `touches` | Deprecated; replaced by `contains_xy`, `intersects_xy` |
| OverlayNG | No — TopologyExceptions on edge cases | Yes — robust, precision-model aware |
| STRtree spatial index | Basic | `query()` with predicate filter + `query_nearest()` |
| Binary wheels on PyPI | Partial | Full (Linux/macOS/Windows) with bundled GEOS |
| API stability | — | Stable; keyword-only deprecations in 2.0, clean in 2.1 |

---

## Migration Notes (1.x → 2.x)

- **Non-breaking path:** upgrade via Shapely 1.8 first (deprecation warnings surface there);
  then move to 2.0 with all warnings fixed.
- **Removed:** `shapely.vectorized`; `prepared.prep()`; several positional-arg signatures now
  keyword-only (`grid_size`, `normalized`, `include_z`, `indices`).
- **Added:** entire `shapely.*` functional namespace mirrors the old OO API but is vectorized.
- GeoPandas migrated from PyGEOS to Shapely 2.0 backend (transparent to users).

---

## Offshore-Relevant Operations

| Use Case | Shapely API |
|---|---|
| Turbine exclusion zones | `shapely.buffer(point_array, radius)` |
| Lease area / polygon overlap | `shapely.intersection(poly_a, poly_b)` — OverlayNG robust |
| Cable corridor geometry | `shapely.buffer(linestring, width)` + `shapely.difference()` |
| Minimum separation checks | `shapely.distance(geom_a, geom_b)` (vectorized over arrays) |
| Nearest turbine / asset | `STRtree.query_nearest()` |
| Restricted zone containment | `shapely.contains(zone_poly, point_array)` |
| Convex hull of array footprint | `shapely.convex_hull(multipoint)` |
| Voronoi / Delaunay for site mesh | `shapely.voronoi_polygons()`, `shapely.delaunay_triangles()` |
| Area / perimeter of layout zones | `.area`, `.length` on Polygon arrays |

**CRS caveat:** Shapely operates on a Cartesian plane only. For metric distance accuracy over
geographic extents, project coordinates first with **pyproj** (e.g., UTM) before passing to
Shapely.

---

## Integration Ecosystem

| Library | Integration |
|---|---|
| **GeoPandas** | Uses Shapely 2.x as its geometry backend (GeoDataFrame.geometry column = Shapely objects) |
| **pyproj** | `pyproj.Transformer.transform()` → feed projected coords into Shapely; no native coupling needed |
| **Rasterio** | `rasterio.features.geometry_mask()` and `rasterio.features.shapes()` accept/return Shapely geometries |
| **Fiona / PyOGIO** | I/O layer; reads/writes GeoJSON/shapefiles as Shapely geometry dicts |
| **NumPy** | First-class — geometry arrays are typed NumPy object arrays; ufuncs broadcast naturally |
| **SciPy / scikit-image** | No native coupling; hand-off via coordinate arrays |

Binary wheels bundle GEOS — `pip install shapely` is sufficient on all three platforms.
No system-level GEOS installation required.

---

## Recommendation

**Adopt.**

Shapely 2.x is the correct primitive geometry layer for offshore site layout work.
It covers every core spatial operation needed (buffers, intersections, distances, spatial
indexing), ships pre-built with GEOS bundled, integrates cleanly with the rest of the
geospatial Python stack (GeoPandas, pyproj, Rasterio), and has a stable, well-documented
API. The 2.x vectorized interface removes the only meaningful performance concern of 1.x.
No viable lighter-weight alternative exists for this class of planar geometry problems.

**One-liner verdict:** Shapely 2.x is production-ready planar geometry for offshore site
layout — adopt immediately as the geometry primitive beneath any GIS or layout module.

---

## Sources

- [Shapely 2.1.2 release notes](https://shapely.readthedocs.io/en/stable/release/2.x.html)
- [Shapely installation / binary wheels](https://shapely.readthedocs.io/en/stable/installation.html)
- [Shapely buffer reference](https://shapely.readthedocs.io/en/stable/reference/shapely.buffer.html)
- [GeoPandas migration from PyGEOS to Shapely 2.0](https://geopandas.org/en/latest/docs/user_guide/pygeos_to_shapely.html)
- [GeoPandas installation (binary wheels)](https://geopandas.org/en/stable/getting_started/install.html)
- [WES 2024 — Optimizing offshore wind export cable routing using GIS](https://wes.copernicus.org/articles/9/1105/2024/)
- [Youwind — Buffer and Exclusion Zones in Wind Farm Layout](https://youwindrenewables.com/knowledge-center/buffer-exclusion-zones-gis-wind-farm-layout/)
