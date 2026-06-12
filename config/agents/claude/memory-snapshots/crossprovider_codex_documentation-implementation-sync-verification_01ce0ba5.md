---
name: crossprovider codex documentation-implementation-sync-verification
description: Documentation-implementation sync verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, enforcement, testing]
---

Documented policies (e.g., enforcement env vars, hook behavior, config flags) frequently diverge from actual runtime implementation. Adversarial review must verify both sides: documented contract AND actual implementation. This gap is a class of defect worth surfacing early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
