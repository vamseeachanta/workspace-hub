---
name: crossprovider codex pytest-startup-overhead-in-this-repository
description: pytest startup overhead in this repository
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, performance, environment]
---

Repository test startup (import + plugin init) takes 60–120 seconds before collection completes. Slow execution may be environmental, not code failures. Use bounded timeouts and retry with clean processes. Plugin-disabled runs sometimes bypass contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
