---
name: crossprovider gemini shut-in-detection-via-days-on-production-activit
description: Shut-in detection via days-on-production activity threshold
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-validation, production-analysis, filtering]
---

Filter production records where days_on_prod < threshold (e.g., 5 days) to exclude brief shutdowns and rate artifacts. Threshold is domain-specific; useful for decline curve and fatigue analysis.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
