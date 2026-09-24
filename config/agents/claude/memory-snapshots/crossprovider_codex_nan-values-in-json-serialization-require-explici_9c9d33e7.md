---
name: crossprovider codex nan-values-in-json-serialization-require-explici
description: NaN values in JSON serialization require explicit allow_nan=False
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, json-serialization, gotcha]
---

pandas NaN values are not valid JSON and will fail JSON.parse in browsers or Node.js. Use json.dumps(..., allow_nan=False) when serializing DataFrames to JSON sidecars or embedded HTML payloads to catch the error at generation time rather than runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
