---
name: crossprovider codex toctou-race-in-sequential-read-check-write-witho
description: TOCTOU race in sequential read-check-write without file lock
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [concurrency, data-safety, file-operations]
---

Queue/config mutation guards that hash-check then perform full writes have a data-loss window if appends occur between the check and write (e.g., mechanical_extract._append_csv() ignored lock in llm-wiki #291). Use fcntl/flock or atomic-rename-with-temp-file to close the gap; hash-check-then-write is not safe for concurrent writers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
