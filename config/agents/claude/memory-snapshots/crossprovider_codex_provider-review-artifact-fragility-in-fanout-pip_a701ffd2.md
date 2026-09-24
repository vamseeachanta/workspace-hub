---
name: crossprovider codex provider-review-artifact-fragility-in-fanout-pip
description: Provider review artifact fragility in fanout pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-pipeline, fanout, provider-integration]
---

Provider CLI review outputs (especially Gemini without trust flag) can emit empty or missing artifacts. Consumers must treat missing/empty provider files as UNAVAILABLE-equivalent and avoid inferring approval from disagreement files alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
