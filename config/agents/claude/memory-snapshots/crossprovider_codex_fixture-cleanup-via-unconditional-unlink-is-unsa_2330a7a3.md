---
name: crossprovider codex fixture-cleanup-via-unconditional-unlink-is-unsa
description: Fixture cleanup via unconditional unlink is unsafe
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, fixtures, cleanup]
---

Tests that write to fixed repo fixture paths and unconditionally unlink them in teardown can destroy pre-existing fixture content. Use isolated temp directories (tempfile.TemporaryDirectory or pytest tmp_path) instead of unconditional repo-path cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
