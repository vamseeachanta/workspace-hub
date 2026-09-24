---
name: crossprovider gemini building-count-delta-noise-filter-minimum-3-chan
description: Building count delta noise filter (minimum ≥3 change to trigger event)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [time-series, noise-filtering, threshold]
---

In time-series building-count comparison, filter spurious small changes by requiring |Δ building_count| ≥ 3 before generating a DevelopmentChange event. Threshold is domain-specific (development signals must be substantial) and prevents sensitivity to OSM record drift.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
