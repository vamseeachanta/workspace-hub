---
name: crossprovider gemini audit-trail-use-append-only-event-logs-instead-o
description: Audit trail: use append-only event logs instead of mutable state files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [harness-design, audit, immutability]
---

Replace mutable state files with append-only `events[]` structures (e.g., `user-review-publish.yaml` with time-ordered event entries). Preserves staleness detection, prior decisions, and audit trails; prevents accidental overwrites and enables deterministic 'current state' queries from immutable history.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
