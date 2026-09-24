---
name: crossprovider codex encrypted-pdfs-become-metadata-only-stubs-never-
description: Encrypted PDFs become metadata-only stubs, never extracted content
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, encryption, privacy, standards]
---

Never extract content from encrypted documents. Create a minimal metadata stub (YAML/frontmatter only) with title, code_id, publisher, revision, source_pdf, and `license_status: encrypted-metadata-only`. This preserves provenance while respecting encryption without violating security constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
