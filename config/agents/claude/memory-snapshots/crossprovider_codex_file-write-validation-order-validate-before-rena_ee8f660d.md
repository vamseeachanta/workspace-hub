---
name: crossprovider codex file-write-validation-order-validate-before-rena
description: File-write validation order: validate before rename, catch all errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-handling, validation, error-handling, correctness]
---

Validate content (HTTP status, content-type, size, checksum) BEFORE renaming to final path. Also catch all error types (HTTPError, timeout, TLS, DNS), not just HTTP exceptions. Leaving partial/corrupt files on disk is a correctness and security risk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
