---
name: crossprovider gemini test-first-for-timeout-sensitive-code
description: Test-first for timeout-sensitive code
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, timeout, tdd, stubs]
---

Write tests for timeout and deadline logic BEFORE implementing. Use stub or fake subprocesses to avoid real dependencies and enable deterministic testing of exit codes, process cleanup, and detection behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
