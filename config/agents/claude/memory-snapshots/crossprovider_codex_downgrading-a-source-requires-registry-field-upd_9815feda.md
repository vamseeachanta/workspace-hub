---
name: crossprovider codex downgrading-a-source-requires-registry-field-upd
description: Downgrading a source requires registry field updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-model, source-tracking, backwards-compat]
---

When relegating a prior primary source to 'corroborating evidence only,' ensure structured registry fields (`source_url`, `source_class`) point to the actual new primary source, not the old one. Descriptive notes alone do not update machine-readable routing or downstream report validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
