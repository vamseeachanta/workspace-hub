---
name: crossprovider hermes git-lock-accumulation-under-heavy-parallel-load
description: Git lock accumulation under heavy parallel load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-performance, parallel-load, concurrency]
---

Long sessions with >20 concurrent git processes accumulate zombie `git status` instances that block commits. Under parallel-git storms, chain commands atomically per-file using `;` separators instead of `&&`; avoids chain-break hangs. 19-minute D-state stall observed on workspace-hub.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
