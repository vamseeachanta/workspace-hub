---
name: crossprovider codex operational-metrics-claims-require-non-empty-evi
description: Operational metrics claims require non-empty evidence registry
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, sampling, evidence-gates, metrics]
---

Plans cannot assert yield % or coverage % for ingestion until `trusted-evidence-registry.json` contains seed entries. Empty registry + claimed metrics = MAJOR defect. Defer all operational measurements to metadata-only or block until evidence infrastructure exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
