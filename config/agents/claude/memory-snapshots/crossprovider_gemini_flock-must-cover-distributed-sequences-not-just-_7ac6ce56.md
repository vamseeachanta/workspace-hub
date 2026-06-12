---
name: crossprovider gemini flock-must-cover-distributed-sequences-not-just-
description: Flock must cover distributed sequences, not just final write
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, atomicity, shell-scripting]
---

When atomically writing results of distributed operations (e.g., flock + next-id.sh + file write), the lock must encompass the ENTIRE sequence. WRK-1090 had flock only on final write; concurrent calls to next-id.sh can race and assign duplicate IDs. Lock must be held from id-generation through file write.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
