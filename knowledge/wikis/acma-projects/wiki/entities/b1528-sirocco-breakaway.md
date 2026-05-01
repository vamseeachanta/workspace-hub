---
title: B1528 SIROCCO Breakaway
tags: [project, vessel, naval-architecture, hydrodynamics, rudder, yaw-moment]
added: 2026-05-01
last_updated: 2026-05-01
sources:
  - github://vamseeachanta/acma-projects/B1528/ref/SIROCCO breakaway notes.docx
  - github://vamseeachanta/acma-projects/B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx
  - github://vamseeachanta/acma-projects/B1528/excel_to_py/rudder_force_yaw_moment.py
domain: acma-projects
cross_links:
  - ../sources/b1528-rudder-force-yaw-moments-workbook.md
  - ../sources/b1528-sirocco-breakaway-notes.md
  - ../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md
---

# B1528 SIROCCO Breakaway

B1528 is the ACMA project for the **SIROCCO vs Crescent Towing Breakaway at CMT case**. Source files in `vamseeachanta/acma-projects` use the vessel spelling **SIROCCO/Sirocco**; treat the user spelling “Sorrocco” as an alias until corrected by project records.

## Project source-of-record paths

- `B1528/ref/SIROCCO breakaway notes.docx`
- `B1528/ref/ECDIS Mar 26 Midnight LT.docx`
- `B1528/ref/Rudder Force & Yaw Moments.xlsx`
- `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx`
- `B1528/excel_to_py/rudder_force_yaw_moment.py`
- `B1528/excel_to_py/27. SIROCCO-000272-GA Plan.pdf`

Local repo sync was still in progress/stuck when this page was created, so the evidence was read from GitHub API/raw downloads rather than the local `acma-projects` checkout.

## Principal particulars captured from workbook

From `Rudder Area and Ctr` sheet:

| Quantity | Value | Units | Evidence |
|---|---:|---|---|
| LBP | 225.5 | m | `D7` |
| Breadth molded | 32.26 | m | `D8` |
| Depth molded | 20.02 | m | `D9` |
| Design draft | 12.2 | m | `D10` |
| Rudder area | 44.9395631937 | m² | `C25` |
| Rudder center aft of AP | -1.0520261379 | m | `C26` |
| Rudder center at frame | -1.4027015172 | frame | `C27` |

## Incident/time-trace evidence anchors

`SIROCCO breakaway notes.docx` contains narrative time-trace / benchmark evidence including:

- Prior to breakaway: heading `337.7 deg`, rudder `P 1.1 deg`, STW `4.0 kts` per SIROCCO VDR note.
- ECDIS/video-derived sequence around `02:22:11` to `02:40:29`: heading ranged about `342 deg` to `3 deg` while slowly moving astern.
- Last `6.6 min` of that frame: heading `342–350 deg`, COG due south, average speed `0.77 kn`.
- Full starboard rudder and dead slow ahead period: source narrative states full starboard rudder was held for `4 min 50 s` with main engine dead slow ahead at `40 rpm`; ship sheared to starboard.
- Video-derived benchmark snippets include heading/speed estimates such as `02:47:20` speed `4.14 mph` at about `60 deg` to local river direction, `02:48:20` speed `4.60 mph` at about `15 deg`, `02:48:46` speed `3.68 mph` at about `5 deg`, and `02:50:08` speed `0 mph`.

These are benchmark evidence, not yet a clean numerical validation dataset. A downstream plan should extract them into a structured time-series table with uncertainty notes before using them to calibrate or judge a model.

## Related pages

- [B1528 rudder force/yaw moments workbook](../sources/b1528-rudder-force-yaw-moments-workbook.md)
- [B1528 SIROCCO breakaway notes](../sources/b1528-sirocco-breakaway-notes.md)
- [B1528 SIROCCO rudder yaw-moment inputs](../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md)
