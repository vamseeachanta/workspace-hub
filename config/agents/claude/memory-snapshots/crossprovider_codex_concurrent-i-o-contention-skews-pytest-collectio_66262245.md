---
name: crossprovider codex concurrent-i-o-contention-skews-pytest-collectio
description: Concurrent I/O contention skews pytest collection timing by 10x
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, performance-measurement, ntfs-fuse, methodology]
---

On NTFS-FUSE, concurrent pytest/traversal work inflates timing variance. Use a trivial-file baseline (one empty test file) to isolate genuine hangs from I/O latency; isolated runs can be an order of magnitude faster than contaminated ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
