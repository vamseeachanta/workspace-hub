---
name: crossprovider codex toctou-window-between-attestation-and-execution
description: TOCTOU window between attestation and execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, file-handling, attestation]
---

When a manifest hashes/validates a file in one operation and later code reads or executes that file, concurrent replacement can produce attestation of content A with execution of content B. Hash and parse the same file descriptor; open with `O_NOFOLLOW` to prevent TOCTOU races in attestation workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
