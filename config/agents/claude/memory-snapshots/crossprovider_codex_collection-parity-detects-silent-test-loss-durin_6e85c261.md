---
name: crossprovider codex collection-parity-detects-silent-test-loss-durin
description: Collection parity detects silent test loss during refactor
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [testing, refactoring, regression]
---

When restructuring test files, verify normalized test node IDs and collected case counts remain identical before and after. This catches silent loss of test functions/fixtures that would not be caught by assertion/decorator counts alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
