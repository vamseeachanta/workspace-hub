---
name: crossprovider codex privacy-preserving-ingest-canary-pattern-for-ext
description: Privacy-preserving ingest canary pattern for external datasets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integration, privacy, patterns]
---

When integrating external data with missing content hashes or anonymized titles, use metadata-only aggregates plus a bounded review queue (10–25 items) followed by human approval before content promotion. Never copy raw untrusted datasets directly to Git. Deferred promotion requires a separately authorized content-promotion issue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
