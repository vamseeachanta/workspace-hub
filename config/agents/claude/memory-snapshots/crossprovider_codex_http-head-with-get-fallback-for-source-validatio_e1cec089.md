---
name: crossprovider codex http-head-with-get-fallback-for-source-validatio
description: HTTP HEAD with GET fallback for source validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, integration, networking]
---

curl --head fails on CDNs and some servers that require GET requests. Always use HEAD with a fallback to bounded GET for link validation to prevent false failures on valid sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
