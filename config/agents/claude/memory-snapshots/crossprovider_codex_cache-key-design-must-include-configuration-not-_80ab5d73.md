---
name: crossprovider codex cache-key-design-must-include-configuration-not-
description: Cache-key design must include configuration, not just resource name
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [caching, architecture, correctness]
---

Caching by resource name alone causes stale-data bugs when sequential operations pass different config (e.g., different fixture files). Cache identity must include path/configuration parameters to ensure each config variant gets its own cached state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
