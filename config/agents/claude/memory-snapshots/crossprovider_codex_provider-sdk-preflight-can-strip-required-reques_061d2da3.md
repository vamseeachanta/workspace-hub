---
name: crossprovider codex provider-sdk-preflight-can-strip-required-reques
description: Provider SDK preflight can strip required request fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sdk-bugs, provider-integration, request-validation, streaming]
---

SDK layers that run preflight validation before actual API calls can strip necessary request fields (e.g., `stream: true` for streaming endpoints). Generic connection errors may hide real HTTP 400 status codes from upstream. Verify request payload shape matches endpoint requirements after SDK processing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
