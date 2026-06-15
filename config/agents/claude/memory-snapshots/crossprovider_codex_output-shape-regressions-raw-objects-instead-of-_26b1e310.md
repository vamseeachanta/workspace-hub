---
name: crossprovider codex output-shape-regressions-raw-objects-instead-of-
description: Output shape regressions: raw objects instead of dicts break serialization
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [code-review, serialization, regression-risk]
---

Code changes that emit raw objects (Citation, Result instances) instead of dicts/scalars in output fields break downstream JSON/YAML writers. When refactoring output structures, verify consumers can serialize the new type or emit a dict sidecar—this pattern surfaced in F103 cathodic protection refactor.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
