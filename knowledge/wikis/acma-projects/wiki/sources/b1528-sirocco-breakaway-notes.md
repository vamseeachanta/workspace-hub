---
title: B1528 SIROCCO Breakaway Notes
tags: [source, incident-notes, benchmark, time-trace, naval-architecture]
added: 2026-05-01
last_updated: 2026-05-01
sources:
  - github://vamseeachanta/acma-projects/B1528/ref/SIROCCO breakaway notes.docx
  - github://vamseeachanta/acma-projects/B1528/ref/ECDIS Mar 26 Midnight LT.docx
domain: acma-projects
cross_links:
  - ../entities/b1528-sirocco-breakaway.md
  - ../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md
---

# B1528 SIROCCO Breakaway Notes

Primary narrative source: `B1528/ref/SIROCCO breakaway notes.docx`.

## Extracted benchmark facts for calculation planning

The notes contain qualitative and semi-quantitative time history evidence suitable for structuring a benchmark dataset before numerical model comparison.

### Initial/operating conditions

- Breakaway incident: lower Mississippi River, Convent Marine Terminal, mile marker 160.9, March 27 2023.
- Prior to breakaway: heading `337.7 deg`, rudder `P 1.1 deg`, STW `4.0 kts` per SIROCCO VDR note.
- Current evidence: document references `4.0 kts` current and ECDIS/bridge statements.
- Workbook note: slow ahead at `45 rpm` would make `6.5 kn` fully loaded, but in `4 kn` current the vessel would make only `2.5 kn` effective forward speed.

### Time-trace/benchmark anchors

- `02:22:11`: Sirocco heading upriver with slow astern movement; tug Savannah suggested dropping port anchor.
- Following `18 min`: heading ranged between about `342 deg` and `3 deg` while slowly moving astern.
- Last `6.6 min` before `02:40:29`: heading about `342–350 deg`, COG due south, average speed `0.77 kn`.
- Full starboard rudder and dead slow ahead: narrative states full starboard rudder held for `4 min 50 s` with engine dead slow ahead at `40 rpm`, causing forward/starboard sheering.
- Video-derived later sequence:
  - `02:45:06`: sudden starboard rotation about `20 deg`.
  - `02:47:20`: speed about `4.14 mph`, heading about `60 deg` to local river direction.
  - `02:48:20`: speed about `4.60 mph`, heading about `15 deg` to local river direction.
  - `02:48:46`: speed about `3.68 mph`, heading about `5 deg`.
  - `02:50:08`: speed about `0 mph`, bow moving to port.

## Use in downstream numerical work

These notes should be converted into a structured benchmark table before model validation. The first model comparison should avoid overclaiming because:

- Most headings/speeds are narrative or video-derived estimates, not a clean sensor export.
- The event includes anchors, tugs, current, bank effects, and propulsion/rudder interaction.
- A first-order Nomoto/yaw-moment model can test trend and plausibility, but cannot prove full incident reconstruction.

## Related pages

- [B1528 SIROCCO Breakaway](../entities/b1528-sirocco-breakaway.md)
- [B1528 rudder force/yaw moments workbook](b1528-rudder-force-yaw-moments-workbook.md)
- [B1528 SIROCCO rudder yaw-moment inputs](../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md)
