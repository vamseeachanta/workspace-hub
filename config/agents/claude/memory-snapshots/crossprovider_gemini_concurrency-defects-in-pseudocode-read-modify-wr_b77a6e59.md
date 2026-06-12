---
name: crossprovider gemini concurrency-defects-in-pseudocode-read-modify-wr
description: Concurrency defects in pseudocode: read-modify-write races need explicit locks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, race-conditions, idempotency]
---

Emitters that claim 'idempotency' but perform unguarded read-modify-write cycles (e.g., reading existing file, deduping, writing result) are vulnerable to concurrent runs. Gemini reviews catch these when Claude doesn't. Pseudocode must explicitly state lock mechanism (fcntl.flock, file-based semaphore, atomic file creation) or documented eventual-consistency strategy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
