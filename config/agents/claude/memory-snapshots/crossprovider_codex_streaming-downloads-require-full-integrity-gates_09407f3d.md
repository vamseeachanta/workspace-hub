---
name: crossprovider codex streaming-downloads-require-full-integrity-gates
description: Streaming downloads require full integrity gates, not just checksums
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [reliability, downloads, data-integrity, testing]
---

Systems that stream download content, compute checksums of arrived bytes, then atomically rename are vulnerable to truncation — incomplete downloads appear valid. Pre-download Content-Length assertion or full-archive integrity verification (e.g., archive signature check, not just byte-hash) is required before atomic rename.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
