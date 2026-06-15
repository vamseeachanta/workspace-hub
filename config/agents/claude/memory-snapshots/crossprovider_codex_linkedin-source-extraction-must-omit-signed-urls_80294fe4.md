---
name: crossprovider codex linkedin-source-extraction-must-omit-signed-urls
description: LinkedIn source extraction must omit signed URLs and auth tokens
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [linkedin-extraction, privacy, source-integrity]
---

Extracted LinkedIn sources must strip query tokens, session tokens, signed media URLs, and credentials. If source URL is unavailable, state this plainly in the source page and cite extraction context instead of reconstructing URLs. Maintain traceability via quoted text and platform identifiers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
