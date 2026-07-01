---
name: crossprovider codex multi-wave-ingestion-governance-requires-sequenc
description: Multi-wave ingestion governance requires sequenced approval gates, not flat dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [governance, planning, ingestion-workflow, gate-sequencing]
---

Ingestion workflows with multiple content lanes need a ledger/routing contract (gate 1) before lane plans, then storage/retrieval contract (gate 2) before waves producing outputs. Treat gates as cascading blockers: #51 (ledger) blocks #52-#60 (content), and #61 (storage) blocks any wave that selects/publishes derived artifacts. Flat dependency lists miss this sequencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
