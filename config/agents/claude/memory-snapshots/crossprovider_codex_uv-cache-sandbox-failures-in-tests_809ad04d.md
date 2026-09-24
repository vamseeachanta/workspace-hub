---
name: crossprovider codex uv-cache-sandbox-failures-in-tests
description: uv cache sandbox failures in tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, environment, sandboxing]
---

When `uv run pytest` executes in a sandboxed home context (e.g., `~/.cache/uv` inaccessible), it fails before tests run. This is an environmental blocker, not a test failure; treat as escalation or pre-seed the cache rather than retrying the test.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
