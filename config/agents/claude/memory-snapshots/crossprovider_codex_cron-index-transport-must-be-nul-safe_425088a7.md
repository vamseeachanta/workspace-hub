---
name: crossprovider codex cron-index-transport-must-be-nul-safe
description: Cron index transport must be NUL-safe
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [data-integrity, scheduling]
---

git cat-file --batch without -Z silently truncates on special characters. Use -Z with odd-byte validation and fail-closed fallback to prevent silent data loss in mutation indices.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
