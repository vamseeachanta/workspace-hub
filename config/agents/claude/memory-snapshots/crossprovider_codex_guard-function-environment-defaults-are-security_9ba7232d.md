---
name: crossprovider codex guard-function-environment-defaults-are-security
description: Guard function environment defaults are security-critical
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, guards, environment-variables]
---

When a guard function accepts an optional env parameter, it must read os.environ if env is not supplied. Omitting this silently bypasses ambient security conditions—the guard succeeds even when it should fail based on environment state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
