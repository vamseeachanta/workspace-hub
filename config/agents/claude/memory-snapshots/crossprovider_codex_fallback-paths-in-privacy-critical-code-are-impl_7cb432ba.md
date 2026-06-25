---
name: crossprovider codex fallback-paths-in-privacy-critical-code-are-impl
description: Fallback paths in privacy-critical code are implicit threat surface
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [testing, privacy, fallback-risk, implicit-leak]
---

Happy-path tests can pass while fallback/error paths leak. DNV prompt/draft generators silently emit raw source identity as a fallback when source-root validation fails. Synthetic probes (malformed rows, missing fields, validation failures) and explicit fallback-path coverage are needed for privacy code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
