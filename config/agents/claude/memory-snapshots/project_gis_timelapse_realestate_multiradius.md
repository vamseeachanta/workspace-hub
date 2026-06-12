---
name: project_gis_timelapse_realestate_multiradius
description: gis.imagery timelapse can serve real-estate purchase due-diligence at selectable 2/5/10-mi radii; radii must follow real-estate analysis guidelines
metadata: 
  node_type: memory
  type: project
  originSessionId: 418eae65-b0b5-4afd-ba31-d1663bc3b6ab
---

The digitalmodel `gis.imagery` aerial-timelapse skill has a second use case beyond a single
property: **real-estate acquisition due-diligence videos** showing *area development over
time* around a candidate site at **selectable radii (e.g. 2 / 5 / 10 mile rings)** — built
out, road/retail growth, density change in the surrounding market/trade area.

Key constraint: the **selected radius must be compliant with real-estate analysis
guidelines** (appraisal / market-study / site-selection trade-area rings — commonly 1/3/5
mi + drive-time variants). Don't hard-code; the manifest picks guideline-aligned radii and
the output report records the chosen radii + basis for defensibility.

Needs: generalize the current fixed two scales (property 0.20 mi / neighborhood 1.50 mi) to
an arbitrary `radii_miles` list; larger radii need a multi-tile NAIP mosaic per frame.
Written up in digitalmodel branch `gis-imagery-enhancements`
(`src/digitalmodel/gis/imagery/ROADMAP.md` §5). See
[[feedback_timelapse_append_current_satellite_frame]], [[feedback_gis_imagery_wrong_tile_selection]].
