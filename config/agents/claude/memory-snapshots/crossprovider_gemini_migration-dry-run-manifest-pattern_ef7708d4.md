---
name: crossprovider gemini migration-dry-run-manifest-pattern
description: Migration dry-run manifest pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migrations, safety, checksum-verification, audit-trail]
---

For large file relocations, capture dry-run as manifest with fixed summary-line format (repo=X loc=Y files=Z target=T dry_run=true), parallel checksums (source + target post-apply), collision/duplicate detection, and file counts. Pre-apply gates verify manifest checksums match. Idempotent apply ensures second run is no-op. Provides traceability + safety for unattended migrations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
