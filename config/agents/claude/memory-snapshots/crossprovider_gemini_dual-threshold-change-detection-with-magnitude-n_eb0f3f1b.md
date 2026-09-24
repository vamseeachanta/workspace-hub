---
name: crossprovider gemini dual-threshold-change-detection-with-magnitude-n
description: Dual-threshold change detection with magnitude normalization
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [time-series, change-detection, signal-processing]
---

Detect changes using separate loss and gain thresholds (e.g., NDVI Δ ≤ -0.15 or ≥ +0.15). Normalize magnitude to [0,1] by ratio of change pixels to total pixels. Simplifies signal/noise separation and enables uniform confidence scoring across different change types.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
