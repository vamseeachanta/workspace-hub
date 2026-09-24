---
name: crossprovider codex red-tests-valid-by-interface-inspection-despite-
description: RED tests valid by interface inspection despite runtime blocks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, methodology]
---

When pytest execution hangs (venv import timeouts, permission waits), interface inspection of method signatures and existing call sites can still validate RED test correctness. Trace the expected behavior from the interface and fixtures; executable proof comes later when contention clears.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
