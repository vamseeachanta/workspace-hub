---
name: crossprovider codex atomic-bracketing-of-sensitive-git-operations
description: Atomic bracketing of sensitive Git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-operations, attestation, exception-safety]
---

Writes without bracketing fail-open (intermediate state leaks on exception). Bracket each mutation with independent before-and-after checks; use try/finally for post-operation attestation even on failure paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
