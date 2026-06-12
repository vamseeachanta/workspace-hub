---
name: crossprovider codex hermes-codex-streaming-field-is-now-mandatory
description: Hermes/Codex streaming field is now mandatory
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hermes, codex, api-integration, streaming]
---

Hermes was sending `allow_stream=False` which omits the `stream: true` field required by current ChatGPT Codex versions. The error surfaced as generic `APIConnectionError` instead of the underlying HTTP 400. Streaming support is a hard requirement for Codex integration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
