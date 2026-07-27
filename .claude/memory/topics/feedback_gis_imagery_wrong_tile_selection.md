> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gis_imagery_wrong_tile_selection.md

---
name: feedback_gis_imagery_wrong_tile_selection
description: digitalmodel PR
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 418eae65-b0b5-4afd-ba31-d1663bc3b6ab
---

`digitalmodel.gis.imagery` (PR #621, branch `feat/gis-imagery-timelapse-2538`) NAIP timelapse renderer has two gaps found while running it for FD30150 (15645 Westpark Dr, Houston):

1. **Wrong-tile selection**: it picks a NAIP STAC item that *intersects* the search bbox but does **not contain the property point** (grabbed the `_nw` quarter-quad when the store sits in `_ne`). Result: out-of-the-box frames are centered off-property (showed fields/bayou, not the building).
2. **Neighborhood-scale only**: `frames/property/` is empty by design — only the 1.5 mi neighborhood preview renders, too zoomed to resolve a building.

**Why:** the renderer uses the STAC `rendered_preview` of a representative item per year, with no point-containment check and no property-scale crop.

**How to apply:** select the item with `intersects: {Point}` and verify `bbox` contains the point; for building-level frames, fetch the tiler XYZ tiles (`/api/data/v1/item/tiles/WebMercatorQuad/{z}/{x}/{y}@2x?collection=naip&item=...&assets=image&asset_bidx=image|1,2,3`) at z≈18 and stitch+crop to the property bbox. Texas NAIP is biennial (2012–2022). Pipeline lives in [[project_analysis_domain_objective]]-style output repos; ran fine offline w/ requests+imageio+pillow+pyproj+shapely (no Earth Engine / planetary-computer pkg needed).
