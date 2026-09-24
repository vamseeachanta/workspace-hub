---
name: crossprovider codex live-process-relocation-requires-proc-maps-inspe
description: Live process relocation requires /proc/*/maps inspection, not just /proc/*/exe
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-safety, relocation, file-deletion, live-processes]
---

When relocating a directory containing binaries or libraries that are currently executing, check `/proc/*/maps` for deleted references and dangling shared-object mappings. A process can have its cwd successfully restored but still hold old memory maps to deleted libraries. `.fuse_hidden` tombstones accumulate and cannot be reclaimed until the process exits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
