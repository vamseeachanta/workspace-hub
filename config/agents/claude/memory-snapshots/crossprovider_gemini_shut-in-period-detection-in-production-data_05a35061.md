---
name: crossprovider gemini shut-in-period-detection-in-production-data
description: Shut-in period detection in production data
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bsee-analysis, decline-curves, production-data]
---

BSEE production data needs shut-in filtering before decline curve fitting. Use DAYS_ON_PROD < threshold (e.g., 5 days) to detect shut-in months. Exclude these rows before aggregating rates to avoid noise.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
