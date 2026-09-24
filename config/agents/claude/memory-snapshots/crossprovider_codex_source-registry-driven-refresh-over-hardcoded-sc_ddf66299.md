---
name: crossprovider codex source-registry-driven-refresh-over-hardcoded-sc
description: Source-registry-driven refresh over hardcoded scheduler lists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-pipelines, scheduler, source-management, freshness]
---

Data pipeline freshness systems that hardcode job lists in the scheduler drift when new sources are added. Instead, maintain a source-registry with explicit cadence, refresh-mode (incremental/snapshot/append), and priority; generate scheduler jobs from the registry. Enables staleness tracking, source discovery, and refresh-mode enforcement without code changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
