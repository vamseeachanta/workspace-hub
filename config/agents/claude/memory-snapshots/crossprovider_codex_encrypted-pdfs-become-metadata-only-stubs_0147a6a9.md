---
name: crossprovider codex encrypted-pdfs-become-metadata-only-stubs
description: Encrypted PDFs become metadata-only stubs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [encryption-handling, metadata-preservation, ingest-contract]
---

Don't skip encrypted/DRM PDFs entirely. Create a minimal stub page with code_id, publisher, revision, source_pdf, visibility, and license_status: encrypted-metadata-only. Preserves discoverability without claiming full fidelity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
