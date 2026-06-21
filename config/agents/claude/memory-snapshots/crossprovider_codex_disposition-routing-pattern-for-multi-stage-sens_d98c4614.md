---
name: crossprovider codex disposition-routing-pattern-for-multi-stage-sens
description: Disposition/routing pattern for multi-stage sensitive-document workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [pattern, architecture, o&g-workflows, multi-stage-pipelines]
---

Disposition builders output both JSON metadata (schema, gate_status, counts) and JSONL rows (one per document). Each row carries routing ID, content digest, extension, disposition class, follow-up issue ref, and no-ingest/no-read flags. Disposition class determines next-lane routing. Reuse this pattern for O&G/FDI multi-stage pipelines where safety gates must pass between stages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
