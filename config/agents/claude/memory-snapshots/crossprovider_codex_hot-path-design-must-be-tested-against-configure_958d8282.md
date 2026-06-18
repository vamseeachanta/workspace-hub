---
name: crossprovider codex hot-path-design-must-be-tested-against-configure
description: Hot-path design must be tested against configured timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [performance, timeout, design, testing]
---

Proposed hot-path solutions (e.g., skill lookup in a 5s hook window) must be benchmarked against the actual timeout, not just 'should be fast.' A 28s enumeration will fail in a 5s hook, even if it 'works' in testing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
