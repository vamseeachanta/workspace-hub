> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_timelapse_append_current_satellite_frame.md

---
name: feedback_timelapse_append_current_satellite_frame
description: GIS timelapse videos should append a current high-res satellite/Maps frame as the final frame; NAIP lags ~2-4 yrs (latest 2022)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 418eae65-b0b5-4afd-ba31-d1663bc3b6ab
---

For aerial-imagery timelapse videos (digitalmodel `gis.imagery`), **append the latest
available high-res satellite/Google-Maps-view frame as the final frame**. NAIP lags 2–4
years (latest available was 2022 for FD30150 in May 2026), so the timelapse stops short of
"now" — adding a current frame would have added clarity on the present condition.

**Why:** the whole point is showing change *up to today*; ending at 2022 understates recent
state (e.g., south/east overgrowth as it is now).

**How to apply:** add a recent-imagery frame to the sequence. Source options, in
ToS-preference order: current **NAIP** if newer than cached; **Esri World Imagery** /
**USGS** XYZ tiles (open); Bing/Google Maps satellite only with attention to terms. Stitch
via the same WebMercator tiler approach used for property crops. Label it "current
(<source>, <year>)". Lesson from FD30150 timelapse 2026-05-27. See
[[feedback_gis_imagery_wrong_tile_selection]] and [[project_skestates_facility_evidence_timeline]].
