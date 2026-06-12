---
name: crossprovider gemini yaml-append-operations-require-file-locking-and-
description: YAML append operations require file locking and safe parsing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, file-safety, yaml]
---

Raw text appends to YAML files break document structure under concurrent writes and require flock guards. Prefer JSONL (inherently append-safe) or use yq/structured merge tools. Never rely on indentation-preserving text concatenation for YAML.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
