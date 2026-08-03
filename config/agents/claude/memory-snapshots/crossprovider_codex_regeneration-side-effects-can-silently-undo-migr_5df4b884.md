---
name: crossprovider codex regeneration-side-effects-can-silently-undo-migr
description: Regeneration side effects can silently undo migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [build-system, testing, isolation]
---

Generators and builders can overwrite tracked files during normal output runs. Always regenerate into isolated temp directories and diff against the committed version; separate the drift-detection pass from file writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
