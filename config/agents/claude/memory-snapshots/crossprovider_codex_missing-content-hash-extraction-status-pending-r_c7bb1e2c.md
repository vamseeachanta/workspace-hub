---
name: crossprovider codex missing-content-hash-extraction-status-pending-r
description: Missing content_hash + extraction_status=pending + raw metadata identities = cannot directly ingest to public repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [privacy, data-integration, metadata, security-gate]
---

Large databases with pending extraction status, missing content hashes, and unvalidated raw metadata (paths, titles, descriptions) exposing personal/client/project identities cannot be copied to Git or used for direct wiki generation. Requires read-only adapter, sanitized aggregates, opaque canary queue, and explicit human review before any content promotion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
