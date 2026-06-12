---
name: crossprovider codex format-metadata-must-be-source-backed-not-hardco
description: Format metadata must be source-backed, not hardcoded from convention
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [format-mapping, schema, source-audit]
---

#606 hardcodes `.dat` → `Wamit dat` format mapping, but existing repository specs use `Aqwa dat` for `.dat` meshes. Format identity is correctness-critical; plans must audit existing examples and acceptance tests before fixing format enums.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
