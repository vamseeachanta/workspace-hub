---
name: crossprovider codex dry-run-authoritative-at-permission-level-not-be
description: Dry-run authoritative at permission level, not behavior level
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, idempotency, dry-run]
---

Compute `write = write_files and not dry_run` at write-permission decision, not inside each write call. Prevents accidental mutations when dry_run=True but write_files=True, making dry-run tests safe without mocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
