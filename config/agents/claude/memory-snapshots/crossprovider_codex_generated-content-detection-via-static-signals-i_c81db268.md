---
name: crossprovider codex generated-content-detection-via-static-signals-i
description: Generated-content detection via static signals is incomplete without cardinality analysis
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-content, detection, schema]
---

Lockfile and timestamp detection catch common generated patterns but miss high-cardinality cases (many unique keys/paths in a small file). Effective detection requires both signal-based (known file shapes) and content-analysis-based (key/path cardinality) strategies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
