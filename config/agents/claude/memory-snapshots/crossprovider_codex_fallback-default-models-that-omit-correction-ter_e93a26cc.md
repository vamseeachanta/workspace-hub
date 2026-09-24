---
name: crossprovider codex fallback-default-models-that-omit-correction-ter
description: Fallback/default models that omit correction terms produce silent errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [model-architecture, fallback-paths, subsea-pipeline, seabed-proximity]
---

When simplified fallback models are used (e.g., SpanAllowableLength with fixed Ca=1.0 instead of Ca(e/D)), missing correction terms can overpredict results when injection parameters are absent. Fallback pathways must preserve critical physics corrections or document the approximation impact.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
