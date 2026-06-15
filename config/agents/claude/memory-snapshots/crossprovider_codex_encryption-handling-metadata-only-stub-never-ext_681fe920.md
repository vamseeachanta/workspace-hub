---
name: crossprovider codex encryption-handling-metadata-only-stub-never-ext
description: Encryption handling: metadata-only stub, never extract content
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [encryption, security, privacy, ingest]
---

Encrypted PDF → create a metadata-only source resolver with title, code_id, publisher, revision, and `license_status: encrypted-metadata-only`. Never attempt to extract content from encrypted files; privacy and contract compliance require this boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
