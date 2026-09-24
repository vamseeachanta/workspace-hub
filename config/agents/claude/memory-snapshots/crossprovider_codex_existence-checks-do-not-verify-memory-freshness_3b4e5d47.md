---
name: crossprovider codex existence-checks-do-not-verify-memory-freshness
description: Existence checks do not verify memory freshness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-provider-parity, memory-management, testing]
---

Testing that memory files or state artifacts exist does not catch staleness. For cross-provider parity, explicit freshness verification and critical-content inclusion checks are needed, not just 'non-empty' assertions. Timestamp-based or manifest-based freshness verification is load-bearing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
