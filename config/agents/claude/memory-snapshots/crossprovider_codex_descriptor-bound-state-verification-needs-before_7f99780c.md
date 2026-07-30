---
name: crossprovider codex descriptor-bound-state-verification-needs-before
description: Descriptor-bound state verification needs before/after checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [file-operations, toctou-safety, descriptor-bound, verification]
---

Safe file operations require identity verification before the operation (via fstat after opening by descriptor, comparing with prior stat), during the operation (content hashing with post-hash re-fstat), and after (fstat again to detect concurrent mutations). Single-point stat checks miss TOCTOU races. Store link-count, mode, size, timestamps, and identity for comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
