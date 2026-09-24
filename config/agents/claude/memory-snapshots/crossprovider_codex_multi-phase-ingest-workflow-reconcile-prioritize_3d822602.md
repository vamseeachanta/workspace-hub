---
name: crossprovider codex multi-phase-ingest-workflow-reconcile-prioritize
description: Multi-phase ingest workflow: reconcile → prioritize → canary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest-workflow, governance, lesson-learned]
---

Before extracting large corpora (>4K files), first reconcile counts across catalogs and filesystem to resolve stale estimates; then prioritize by domain value and series authority; then run a small canary batch. Skipping reconciliation leads to scope creep and incomplete coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
