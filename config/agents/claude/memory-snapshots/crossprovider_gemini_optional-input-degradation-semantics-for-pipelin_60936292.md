---
name: crossprovider gemini optional-input-degradation-semantics-for-pipelin
description: Optional input degradation semantics for pipelines
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [config-handling, optional-inputs, pipeline-robustness]
---

Missing optional config inputs don't crash (normal status). If config explicitly requires a surface pattern and it's absent, status = `degraded` (reports emit, approval gates fail). Always document missing surfaces in summary output.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
