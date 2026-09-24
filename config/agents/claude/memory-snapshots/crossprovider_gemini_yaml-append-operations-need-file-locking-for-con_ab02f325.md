---
name: crossprovider gemini yaml-append-operations-need-file-locking-for-con
description: YAML append operations need file locking for concurrent writes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, file-safety, yaml]
---

Raw text append to YAML files (`>> file.yaml`) without flock breaks structure when multiple sessions write concurrently. Indentation and list nesting become corrupt and unparseable. Use `flock -x` around append operations, or switch to JSONL (append-safe by design).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
