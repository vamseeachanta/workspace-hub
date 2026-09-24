---
name: crossprovider codex publishability-requires-status-codes-not-binary-
description: Publishability requires status codes, not binary rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [content-classification, redaction, contracts]
---

Content classification systems must distinguish 'publish-ready' from 'redacted-but-retained' states. Fail-closed rejection of redactable content (private paths, sanitizable leaks) violates redaction contracts. Use status codes or reason tags to encode why content is retained despite privacy issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
