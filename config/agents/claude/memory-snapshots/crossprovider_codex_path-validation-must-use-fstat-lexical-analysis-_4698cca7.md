---
name: crossprovider codex path-validation-must-use-fstat-lexical-analysis-
description: Path validation must use fstat/lexical analysis, never open() on untrusted paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [path-validation, security, DoS]
---

Opening a FIFO with O_RDONLY blocks indefinitely before fstat() can check st_mode and reject it. Device-file security tests must be present; test coverage claims that don't exercise FIFO/device paths are false positives. Use lstat/fstat or lexical basename patterns, never open() as a validation step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
