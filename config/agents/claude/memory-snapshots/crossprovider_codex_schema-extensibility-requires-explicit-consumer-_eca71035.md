---
name: crossprovider codex schema-extensibility-requires-explicit-consumer-
description: Schema extensibility requires explicit consumer-contract clarity
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-evolution, api-contract, backwards-compat]
---

When extending existing structured files (YAML, JSON), clarify whether new fields coexist with old or replace them. Example: adding drift block to ai-tools-status.yaml while preserving per-machine tools section requires stating old readers continue to work or explicitly bump the schema version. Silent contracts cause downstream breakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
