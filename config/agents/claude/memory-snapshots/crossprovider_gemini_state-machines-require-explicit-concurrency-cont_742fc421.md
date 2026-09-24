---
name: crossprovider gemini state-machines-require-explicit-concurrency-cont
description: State machines require explicit concurrency contract
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, safety]
---

Multi-account state machines need explicit concurrency semantics: fcntl advisory lock + writer-identity stamp + idempotency rules. Prevents corrupt writes and makes concurrent access auditable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
