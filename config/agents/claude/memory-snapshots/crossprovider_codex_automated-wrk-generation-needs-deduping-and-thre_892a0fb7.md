---
name: crossprovider codex automated-wrk-generation-needs-deduping-and-thre
description: Automated WRK generation needs deduping and thresholds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, quality-gates, work-queue, churn-prevention]
---

Detectors that emit WRKs automatically (e.g., doc drift, quality checks) must include guards to prevent churn: minimum delta threshold, consecutive-run confirmation, and dedupe against existing open WRKs for the same repo/cause.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
