---
name: crossprovider codex existing-test-fixtures-collide-with-stricter-val
description: Existing test fixtures collide with stricter validation rules at scan time
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, validation, migration]
---

Pre-existing canary files and negative fixtures in the repo will match new deny patterns when full-tree scanning is enabled. Plan migration or forensic allow-contexts for existing matches before enabling strict CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
