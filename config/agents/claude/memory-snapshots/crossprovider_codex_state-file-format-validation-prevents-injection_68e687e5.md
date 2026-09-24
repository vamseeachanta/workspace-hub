---
name: crossprovider codex state-file-format-validation-prevents-injection
description: State file format validation prevents injection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, security, validation]
---

When reading state files, validate format against expected pattern (e.g., regex `^WRK-[0-9]+$`) before using in output. Tampered files can inject terminal control characters; validation gates that risk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
