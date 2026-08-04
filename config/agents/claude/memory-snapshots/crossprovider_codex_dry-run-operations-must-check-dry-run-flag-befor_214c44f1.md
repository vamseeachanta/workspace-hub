---
name: crossprovider codex dry-run-operations-must-check-dry-run-flag-befor
description: Dry-run operations must check DRY_RUN flag before any file writes
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, side-effects, purity, atomicity]
---

Writes to temporary files before the DRY_RUN flag check are observably impure and cause read-only target directories to fail dry-run validation. The flag must gate ALL writes, not just the final rename.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
