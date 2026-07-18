---
name: crossprovider codex transactional-tools-must-refuse-unsafe-overwrite
description: Transactional tools must refuse unsafe overwrites rather than proceed blindly
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [ecosystem-tooling, safety, data-integrity]
---

Reconciliation and ecosystem-mutation tools should detect uncataloged live entries and refuse to overwrite them, signaling the conflict explicitly rather than silently clobbering state. Prefer blocking + audit over destructive correction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
