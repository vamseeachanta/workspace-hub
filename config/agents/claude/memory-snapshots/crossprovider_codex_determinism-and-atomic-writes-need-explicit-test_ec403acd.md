---
name: crossprovider codex determinism-and-atomic-writes-need-explicit-test
description: Determinism and atomic writes need explicit tests, not assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [testing, tdd, determinism, reliability]
---

Code that embeds `date.today()` is not deterministic across runs. Code that writes directly to a target file is not atomic if interrupted. Don't declare determinism or atomicity as acceptance criteria without tests that verify both. Existing code that 'looks' correct often isn't.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
