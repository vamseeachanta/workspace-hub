---
name: crossprovider codex test-reproducibility-requires-validating-product
description: Test reproducibility requires validating production default path
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, reproducibility, integration]
---

Regression tests should validate the actual default CLI entrypoint, not hand-built fixtures. When tests inject fixtures versus using production defaults, reproducibility can drift silently—the default path may not be exercised at all.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
