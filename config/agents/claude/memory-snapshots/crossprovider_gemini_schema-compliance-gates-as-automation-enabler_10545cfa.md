---
name: crossprovider gemini schema-compliance-gates-as-automation-enabler
description: Schema compliance gates as automation enabler
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [schema, automation, ci-gates, metadata]
---

WRK-185 audit found uneven metadata (missing plan_reviewed, plan_approved, provider, complexity). User proposes schema validation gates in CI. Inconsistent metadata breaks agent routing and cross-review dispatch; compliance gates prevent drift before automation runs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
