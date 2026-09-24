---
name: crossprovider codex human-facing-repo-artifacts-must-not-expose-raw-
description: Human-facing repo artifacts must not expose raw local paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [leak-prevention, privacy, data-handling]
---

Paths like `/mnt/ace` belong only in private manifests. Never expose them in `docs/research/` or other human-facing repo artifacts; summarize with source URLs and filters instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
