---
name: crossprovider codex live-endpoint-verification-catches-documentation
description: Live endpoint verification catches documentation-code mismatches that static review misses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, live-code-probes]
---

Static code review of a catalog marking URLs as 'direct_http' artifact downloads missed that configured endpoints actually returned HTML landing pages. Live curl -L -I testing revealed the protocol mismatch. Code and tests passed using fake bytes, but the real transport layer was broken. Include live endpoint verification (HEAD requests with timeout) for network/fetch-based code paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
