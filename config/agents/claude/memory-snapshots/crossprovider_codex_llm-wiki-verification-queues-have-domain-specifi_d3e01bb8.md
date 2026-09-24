---
name: crossprovider codex llm-wiki-verification-queues-have-domain-specifi
description: llm-wiki verification queues have domain-specific schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, data-integrity, schema-design]
---

Different wikis use different CSV shapes: pipeline-engineering (6-column with source_pdf/source_page), geotechnical/offshore/production (4-column), ABS (separate source-id schema). Row-level changes must preserve schema identity; rewrite tests check both schema and row count to prevent silent corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
