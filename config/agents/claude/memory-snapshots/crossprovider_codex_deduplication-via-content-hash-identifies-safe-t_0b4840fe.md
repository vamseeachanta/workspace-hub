---
name: crossprovider codex deduplication-via-content-hash-identifies-safe-t
description: Deduplication via content hash identifies safe-to-exclude staging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, data-cleanup, staging-identification]
---

Large 'raw' or 'staging' directories often duplicate organized publisher dirs entirely. Verify via SHA-256 content hashing rather than filename. If 100% of staging PDFs match organized-dir content, staging is safe to exclude from ingest; caveat: content duplication doesn't prove metadata/path identity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
