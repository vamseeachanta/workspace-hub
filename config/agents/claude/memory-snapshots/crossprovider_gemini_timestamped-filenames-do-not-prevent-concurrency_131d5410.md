---
name: crossprovider gemini timestamped-filenames-do-not-prevent-concurrency
description: Timestamped filenames do not prevent concurrency race conditions
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, file-safety, race-condition]
---

Writing to different timestamped files (e.g., `.../2026-04-20-HHMMSS.jsonl`) provides zero concurrency protection—parallel processes both scan and write, creating duplicates. Use atomic file creation, deterministic filenames with filesystem locks (fcntl.flock), or replace-by-key patterns with explicit locking.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
