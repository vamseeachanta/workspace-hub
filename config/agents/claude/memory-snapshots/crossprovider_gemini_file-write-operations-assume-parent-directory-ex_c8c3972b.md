---
name: crossprovider gemini file-write-operations-assume-parent-directory-ex
description: File write operations assume parent directory exists
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, file-io, error-handling]
---

`Path.write_text()` fails silently with FileNotFoundError if parent missing (fresh clones, deleted dirs). Pre-create with `mkdir(parents=True, exist_ok=True)` before write.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
