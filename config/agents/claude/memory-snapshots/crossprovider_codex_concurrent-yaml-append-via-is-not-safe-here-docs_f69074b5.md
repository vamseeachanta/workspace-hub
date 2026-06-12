---
name: crossprovider codex concurrent-yaml-append-via-is-not-safe-here-docs
description: Concurrent YAML append via >> is not safe; here-docs interleave
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [concurrency, file-io, yaml-safety]
---

Multiple processes appending to the same YAML file using `>>` and here-doc expansion can corrupt the file; the here-doc expands to multiple write syscalls that interleave with concurrent writers. Use atomic file operations (write-then-rename), file locks (flock), or dedicated append scripts with mutual exclusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
