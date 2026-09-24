---
name: crossprovider codex optional-dependency-graceful-degradation-pattern
description: Optional dependency graceful degradation pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, python, resilience, portability]
---

Heavy external dependencies should be made optional via try/except import + feature flag (e.g., HAS_PYPROJ). This allows libraries to function in reduced-feature mode when dependencies aren't available, improving portability across environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
