---
name: crossprovider codex bulk-corpus-ingestion-requires-private-vs-public
description: Bulk corpus ingestion requires private-vs-public gates upfront
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-ingestion, corpus-management, procedural-gate]
---

Before bulk-ingesting sensitive/client content into a shared knowledge base, validate that sanitization gates and private/public separation are enforced at ingestion entry points. Zero corpus success is a signal to establish gates before scaling ingest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
