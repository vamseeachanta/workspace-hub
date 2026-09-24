---
name: crossprovider codex queue-dispatch-requires-real-non-mock-validation
description: Queue dispatch requires real (non-mock) validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, queue-systems, validation, infrastructure]
---

Dispatch plumbing validation with `mock:true` canaries is insufficient. Production readiness requires at least one real end-to-end solve with `mock:false` before operational use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
