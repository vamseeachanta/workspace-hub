---
name: crossprovider codex client-llm-wiki-factory-metadata-only-bootstrap-
description: Client-llm-wiki-factory metadata-only bootstrap is incomplete
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [architecture, factory, registry, technical-debt]
---

Registry accepts empty raw_roots but factory logic, templates, and tests assume a real path. Metadata-only bootstrap fails at runtime. wshub #3449 must plan ingestion-state schema and add bootstrap-without-roots capability before any client can use metadata-only mode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
