---
name: crossprovider codex never-preserve-social-media-authentication-token
description: Never preserve social-media authentication tokens or signed URLs in ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [social-media, security, credential-hygiene]
---

Redact LinkedIn/Twitter/Facebook signed media URLs, session tokens, and query parameters before ingesting extracted content. If source URL is unavailable, cite the extraction context rather than reconstructing or inventing a URL.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
