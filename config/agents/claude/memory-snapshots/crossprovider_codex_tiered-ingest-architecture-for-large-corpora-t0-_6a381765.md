---
name: crossprovider codex tiered-ingest-architecture-for-large-corpora-t0-
description: Tiered ingest architecture for large corpora (T0–T3)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [literature-ingest, architecture, cost-management]
---

For corpora >5K items, split into T0 canary (validation), T1 priority (full-fidelity), T2 selective (abstract-only), T3 metadata-only. Selection criteria per tier: domain-gap match, series authority rank, extraction quality (equations/tables/figures), deduplication rules. Example: 27K+ conference papers split OMAE/OTC first, Flow Induced Vibration as T0 canary, low-signal as T3. Enables controlled scaling and cost management (2026-05-26).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
