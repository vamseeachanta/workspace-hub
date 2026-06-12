---
name: crossprovider hermes route-map-safety-requires-code-data-tests-not-da
description: Route-map safety requires code + data + tests, not data-only fixes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [routing, safety-pattern, code-review]
---

Fixing closed-issue routing in generators via JSON data alone is insufficient if code contains hardcoded fallback routes (e.g., weekly freshness defaults to #76/#79 when JSON missing). Offline-first prevention requires: (1) code-level safe defaults, (2) route-map data changes, (3) regression tests for missing-data scenarios. Validator-only approaches fail in offline/cached generation paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
