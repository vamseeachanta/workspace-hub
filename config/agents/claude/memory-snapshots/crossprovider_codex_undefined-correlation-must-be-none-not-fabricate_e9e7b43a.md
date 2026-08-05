---
name: crossprovider codex undefined-correlation-must-be-none-not-fabricate
description: Undefined correlation must be None, not fabricated as 1.0
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [statistics, correlation, quality-metadata, numerics]
---

Distinct constant arrays or arrays with insufficient variation have undefined correlation (not r=1.0). Marking them IDENTICAL with fabricated correlation defeats quality-of-comparison semantics. Use `np.allclose` before zero-variance checks and preserve `None` for insufficient data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
