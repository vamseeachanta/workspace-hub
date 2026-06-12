---
name: crossprovider gemini dataframe-backed-geospatial-layers-must-validate
description: DataFrame-backed geospatial layers must validate coordinate columns on construction
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [geospatial, validation, dataframe-patterns]
---

FeatureLayer pattern validates that longitude and latitude columns exist at __init__ time, raising KeyError if missing. This early validation prevents silent failures downstream in centroid/bounding-box calculations and makes misconfiguration explicit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
