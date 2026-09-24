---
name: crossprovider gemini fail-closed-import-guards-for-optional-runtime-d
description: Fail-closed import guards for optional runtime dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [error-handling, dependencies, robustness, runtime-safety]
---

Wrap optional imports in try/except ImportError that returns a safe fallback (error message or degraded behavior) rather than crashing. Decouple feature availability from script failure, allowing scripts to run even when optional dependencies are missing from the runtime environment.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
