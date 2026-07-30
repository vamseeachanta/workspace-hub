---
name: crossprovider codex explicit-path-scanners-safer-than-broad-selector
description: Explicit-path scanners safer than broad selectors
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [scanners, safety, evidence]
---

Scanners that fail closed on missing/invalid paths are safer than broad selectors. For plan-review evidence, use explicit `--scan-public-path` arguments pointing to actual artifacts rather than issue selectors that might include future/missing files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
