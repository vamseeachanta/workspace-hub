---
name: crossprovider codex verification-commands-often-miss-config-schedule
description: Verification commands often miss config/scheduler/adapter test surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [testing, verification-gates, test-coverage]
---

When a plan modifies scheduler config, retry logic, adapter fallback paths, or parser boundaries, 'targeted pytest' can pass while omitting those exact test files. Verification lists must enumerate every production/config surface changed and include those test files by full path in the pytest command.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
