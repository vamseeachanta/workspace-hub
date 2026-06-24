---
name: crossprovider codex opaque-handle-sha-256-commitment-architecture-fo
description: Opaque-handle + SHA-256 commitment architecture for private-content batching
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [architecture, privacy, batch-systems]
---

Exact source identifiers stored only in memory during processing; all durable outputs (git diffs, reports, GitHub comments) use opaque handles and non-reversible SHA-256 commitments instead of exact label values. This prevents accidental leaks in unencrypted/logged surfaces.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
