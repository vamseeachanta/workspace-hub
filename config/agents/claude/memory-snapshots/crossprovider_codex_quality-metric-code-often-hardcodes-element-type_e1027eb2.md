---
name: crossprovider codex quality-metric-code-often-hardcodes-element-type
description: Quality metric code often hardcodes element type assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [code-review, assumptions, robustness]
---

Generic code like aspect-ratio calculation assumes quads (4 edges, modulo-4 indexing) but modules may support mixed element types (triangles, quads). Metric code must either handle all types or validate/reject incompatible inputs explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
