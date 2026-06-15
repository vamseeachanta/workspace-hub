---
name: crossprovider codex stale-pointer-detection-beyond-presence
description: Stale pointer detection beyond presence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, pointer-staleness, test-coverage]
---

Tests for 'broken wiki target' only catch missing files. Real gaps: existing-but-stale commit/revision, expired last_checked_at, mismatched content hash, outdated license checks. Add fixtures for each staleness class before integrating pointer validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
