---
name: crossprovider codex ntfs-fuse-concurrent-pytest-runs-invalidate-timi
description: NTFS-FUSE concurrent pytest runs invalidate timing measurements
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [fuse, ntfs, pytest, io-contention, diagnostics]
---

When multiple pytest collection runs execute on the same NTFS-FUSE mount simultaneously, I/O contention severely distorts wall-clock times. A single-file collection can appear to take 54s in concurrent runs but only 4s in isolation. Serialize timed probes on shared FUSE mounts; concurrent runs are valid for existence checks but not for performance data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
