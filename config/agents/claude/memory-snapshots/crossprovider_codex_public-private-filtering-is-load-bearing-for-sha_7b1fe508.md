---
name: crossprovider codex public-private-filtering-is-load-bearing-for-sha
description: Public/private filtering is load-bearing for shared-mount ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [ingestion, shared-storage, security, process]
---

Bulk ingestion from shared mounts requires explicit content filtering to prevent leaking confidential/client material. Treat shared mounts as private-first unless material is explicitly sanitized for publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
