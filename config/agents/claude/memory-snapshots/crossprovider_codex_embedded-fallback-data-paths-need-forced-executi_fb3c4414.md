---
name: crossprovider codex embedded-fallback-data-paths-need-forced-executi
description: Embedded/fallback data paths need forced-execution tests or stay stale
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [testing, fallback-paths, data-staleness]
---

Adapters with hardcoded embedded rows or monkeypatched fallback paths won't reveal staleness if tests use the normal primary path. Plans must explicitly force the fallback (via import failure, condition force, or primary-path deletion) and verify the fallback was actually executed, not just claimed in prose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
