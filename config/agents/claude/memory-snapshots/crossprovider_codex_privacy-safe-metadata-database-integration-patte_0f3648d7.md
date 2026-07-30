---
name: crossprovider codex privacy-safe-metadata-database-integration-patte
description: Privacy-safe metadata database integration pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [data-integration, privacy, metadata]
---

Large metadata databases containing personal/client/commercial identities (e.g., 1.34M+ rows) cannot be directly promoted to Git. Integration requires read-only adapter producing sanitized aggregates, opaque canary queue for human review, and separate approval issue—not direct ingestion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
