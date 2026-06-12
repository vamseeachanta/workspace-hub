---
name: crossprovider hermes google-earth-historical-imagery-api-limitation
description: Google Earth historical imagery API limitation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gis, satellite-imagery, api-limitation]
---

Google Earth Pro's historical imagery is not exposed via public API for automated frame export. For property-level timeline GIFs, practical workflows are: (A) manual Google Earth Pro capture + stitch, or (B) open-data reconstruction using Landsat/Sentinel/NAIP. NAIP aerial (0.6–1m resolution, ~2003–present) is best open-source option for property+lot detail.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
