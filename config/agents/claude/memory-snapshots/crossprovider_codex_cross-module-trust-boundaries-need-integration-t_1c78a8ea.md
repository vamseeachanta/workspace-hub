---
name: crossprovider codex cross-module-trust-boundaries-need-integration-t
description: Cross-module trust boundaries need integration testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [integration-testing, security, module-boundaries]
---

When one module delegates security-relevant behavior (e.g., path safety) to a helper from another module, the integration boundary must have explicit tests documenting the delegated behavior (e.g., symlink-resolution policy), not assume downstream module invariants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
