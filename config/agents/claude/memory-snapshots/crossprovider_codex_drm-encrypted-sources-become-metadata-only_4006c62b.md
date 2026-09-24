---
name: crossprovider codex drm-encrypted-sources-become-metadata-only
description: DRM/encrypted sources become metadata-only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [policy, content-licensing, ingest-workflow]
---

Sources with copy protection or DRM must not be fully extracted; capture only publisher, title, citation, jurisdiction, and off-repo path. Verify DRM status via pdfinfo before planning extraction; do not assume unencrypted without verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
