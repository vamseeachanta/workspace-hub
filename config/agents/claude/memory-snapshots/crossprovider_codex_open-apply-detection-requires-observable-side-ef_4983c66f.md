---
name: crossprovider codex open-apply-detection-requires-observable-side-ef
description: Open/apply detection requires observable side-effects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, security, adversarial]
---

Include path validation cannot assume absence of opens/applies from missing-file errors alone. Use observable detectors: sentinels, FIFOs, helper payload traces, or instrumented open/apply detection. Absence of error ≠ absence of attempt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
