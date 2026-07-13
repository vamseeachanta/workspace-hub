---
name: crossprovider codex fuse-mount-slowness-fallback-probe-strategy
description: FUSE mount slowness → fallback probe strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [infrastructure, git, error-handling]
---

When git/du operations timeout on slow FUSE mounts, switch to direct `.git` metadata + `/proc` evidence instead of inferring clean/ahead state. Distinguish unavailable/unknown from false-green; don't skip probes silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
