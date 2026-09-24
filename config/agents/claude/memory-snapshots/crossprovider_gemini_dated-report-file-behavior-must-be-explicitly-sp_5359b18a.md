---
name: crossprovider gemini dated-report-file-behavior-must-be-explicitly-sp
description: Dated report file behavior must be explicitly specified in specs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [spec-clarity, reporting, automation]
---

When generating timestamped reports (e.g., `dep-health-2026-03-09.yaml`), the behavior on re-runs the same day (overwrite vs append vs fail) must be explicit in the spec. Implicit defaults lead to silent data loss or confusion in automated pipelines.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
