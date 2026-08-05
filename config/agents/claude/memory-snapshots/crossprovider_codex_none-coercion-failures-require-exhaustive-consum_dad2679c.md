---
name: crossprovider codex none-coercion-failures-require-exhaustive-consum
description: None coercion failures require exhaustive consumer tracing
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [debugging, None-handling, data-flow]
---

When optional values (None) enter output-serialization paths, `:.4f`, `np.mean()`, `float(None)`, and `np.isfinite()` all crash silently. Fixing the source is insufficient; audit must trace every consumer (HTML formatters, YAML/JSON serializers, derived metrics) to find coercion sites that weren't obvious.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
