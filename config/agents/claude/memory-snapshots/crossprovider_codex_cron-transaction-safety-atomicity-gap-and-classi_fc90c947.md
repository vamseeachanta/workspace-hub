---
name: crossprovider codex cron-transaction-safety-atomicity-gap-and-classi
description: Cron-transaction safety: atomicity gap and classification precedence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, atomicity, classification-order, safety]
---

Cron-apply missing flock/fcntl.flock() means compare-and-swap isn't atomic; concurrent writes can clobber. Classification checks `cataloged` before `preserved_external`, allowing externally-owned lines to be misclassified and dropped instead of preserved. Put preservation checks first in precedence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
