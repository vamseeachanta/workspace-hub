---
name: crossprovider gemini water-depth-classification-thresholds-for-rig-ty
description: Water depth classification thresholds for rig type inference
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [domain-knowledge, rig-classification, data-validation, drilling-rigs]
---

When explicit rig type is unavailable or requires validation: ≤500 ft → jack_up, 500–10000 ft → semi_submersible, ≥10000 ft → drillship. Use these thresholds to infer RIG_TYPE from WATER_DEPTH_RATING_FT and as a cross-check (mismatch signals data quality issues).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
